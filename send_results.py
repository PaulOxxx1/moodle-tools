"""Basic script for sending out mass-emails with corrected homework.

Copyright (C) 2021  Paul Orschau

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import argparse
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from getpass import getpass
from pathlib import Path
from textwrap import dedent

import markdown
import pandas as pd

from utils import str2bool

# parameters
AUTHOR = 'Paul'
SENDER_EMAIL = "paul.orschau@rwth-aachen.de"
ACCOUNT = "ai479519@rwth-aachen.de"
SERVER = "mail.rwth-aachen.de"
PORT = 587  # for starttls
FILENAME_TEMPLATE = "corrected_{idx:02}.pdf"
SUBJECT = "Mathe Hausaufgabe {idx} wurde korrigiert"
TEMPLATE = """
### Hallo {first}!

Hier ist deine korrigierte Mathe Hausaufgabe {idx}.

Deine Gruppe bestand aus:

{name_list}

Deine Gruppe hat diese Woche folgende Punktzahlen erreicht:

| Aufgabe | Punkte |
| :---- | ----: |
| 1 | {points_1} |
| 2 | {points_2}  |
| 3 | {points_3}  |
| 4 | {points_4}  |
| ∑ | {sum} |

Bei Rückfragen zur Korrektur kannst du mir gerne eine Email schreiben, 
zum Beispiel indem du einfach auf diese Email antwortest.

Gruß

{author}
"""


# parse input args
parser = argparse.ArgumentParser(
    description='Script for sending out corrected homework PDFs and results to students.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--root_folder', 
    required=True,
    help="path of the base folder in which to look for student's folders. should have structure as "
         "downloaded from Moodle, especially the naming scheme of the subfolders.",
)
parser.add_argument(
    '--results_csv',
    required=True,
    help="path of the CSV file created from my numbers spreadsheet, which contains the results.",
    type=str,
)
parser.add_argument(
    '--hw_index',
    required=True,
    help="index of homework to send results for, e.g. 2 for 'HA02'.",
    type=int,
)
parser.add_argument(
    '--debug', type=str2bool, nargs='?', const=True, default=True,
    help="whether to use debug mode. the script won't actually send any emails in this mode.",
)
parser.add_argument(
    '--send_all_emails_to', 
    help="send all emails to this address instead of the student's addresses. "
         "use this e.g. for testing/debugging.",
    type=str,
)
args = parser.parse_args()


def main():
    # get index of current homework
    idx = args.hw_index
    assert idx > 0
    assert isinstance(idx,int)
    print(f"Starting distribution of homework", idx)

    # prepare folder with PDFs
    root = Path(args.root_folder)
    if not root.exists() or not root.is_dir():
        raise RuntimeError("Invalid `root_folder` given.")

    # read results csv
    res_file = Path(args.results_csv)
    if not res_file.exists():
        raise RuntimeError("Invalid `results_csv` given.")
    df = pd.read_csv(
        res_file, 
        sep=';', 
        header=[0,1], 
        skipfooter=2,
        decimal=',',
        na_values='-',
        engine='python',)
    
    # get latest/current group composition for this homework
    grp_key = None
    for i in range(1,idx+1):
        curr_key = ('Gruppe', str(i))
        if curr_key in df:
            grp_key = curr_key

    # get email credentials
    password = getpass(f"Enter your password for the account {ACCOUNT} on server {SERVER}: ")

    # log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP("mail.rwth-aachen.de", port=PORT) as server:
        server.starttls(context=context)
        server.login(ACCOUNT, password)

        # process one group at a time
        for grp, rows in df.groupby(by=grp_key):
            grp = int(grp)
            print(f"Processing group:", grp)

            # find student folder for this group
            folder = None
            folders = []
            for _, row in rows.iterrows():
                row = row.droplevel(1) # use simple index
                name = row['Name']
                temp = list(root.glob(str(name) + '*'))
                if len(temp) > 1:
                    raise RuntimeError("More than one folder for a last name!", name)
                if len(temp) == 1:
                    folders.append(temp[0])
            if len(folders) == 0:
                # no folder for this group found
                print(f"Group {grp} did not have a folder/pdf! Skipping ...")
                continue
            else:
                if len(folders) > 1:
                    raise RuntimeError("More than one folder for a group!", grp)
                folder = folders[0]

            # find PDF for this group
            pdf = None
            pdfs = list(folder.glob('*.pdf'))
            if len(pdfs) != 1:
                raise RuntimeError("Either no or too many PDFs in a folder!", folder)
            pdf = pdfs[0]

            # one group member at a time
            for _, row in rows.iterrows():
                # get student name
                name = row.droplevel(1)['Name']
                print("-- ", name)

                # warning if CSV is potentially outdated, i.e. does not contain records 
                # for this homework
                if (str(idx),'1') not in row:
                    raise RuntimeError("The CSV file does not contain any points for the current "
                                       "homework! (Might be outdated...")

                # compose email
                last, first = name.split(', ')
                team_names = [row.droplevel(1)['Name'] for _,row in rows.iterrows()]
                name_list = '\n'.join(['- ' + name for name in team_names])
                body = TEMPLATE.format(
                    first=first,
                    name_list=name_list,
                    idx=idx,
                    points_1=row[(str(idx), '1')] if (str(idx), '1') in row else '-',
                    points_2=row[(str(idx), '2')] if (str(idx), '2') in row else '-',
                    points_3=row[(str(idx), '3')] if (str(idx), '3') in row else '-',
                    points_4=row[(str(idx), '4')] if (str(idx), '4') in row else '-',
                    sum=row[(str(idx),'∑')],
                    author=AUTHOR,
                )
                html = markdown.markdown(dedent(body), extensions=['tables'])

                # create a multipart message and set headers
                message = MIMEMultipart()
                message["From"] = SENDER_EMAIL
                message["Subject"] = SUBJECT.format(idx=idx)
                message["Bcc"] = SENDER_EMAIL  # TODO

                # add body to email
                message.attach(MIMEText(html, "html"))

                # open PDF file in bindary mode
                with open(pdf, mode='rb') as attachment:
                    # add file as application/octet-stream
                    # email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # encode file in ASCII characters to send by email    
                encoders.encode_base64(part)
                # add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {FILENAME_TEMPLATE.format(idx=idx)}",
                )

                # add attachment to message and convert message to string
                message.attach(part)
                text = message.as_string()

                # get adress
                if args.send_all_emails_to is not None:
                    receiver_email = args.send_all_emails_to # overwrite address
                else:
                    receiver_email = row.droplevel(1)['Email']

                # send email
                if args.debug:
                    print("Debug mode on. Would have sent email to: ", receiver_email)
                else:
                    server.sendmail(SENDER_EMAIL, receiver_email, text)

    print("Done!")

    

if __name__ == '__main__':
    # license
    print(dedent("""
    send_results.py  Copyright (C) 2021  Paul Orschau
    This program comes with ABSOLUTELY NO WARRANTY; for details see `LICENSE` file.
    This is free software, and you are welcome to redistribute it
    under certain conditions; for details see `LICENSE` file.
    """))

    main()
