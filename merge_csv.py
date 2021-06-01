"""Basic script for merging csv files for Moodle upload.

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
from pathlib import Path
from textwrap import dedent

import pandas as pd

from utils import rename_unnamed

# parameters
# ...


# parse input args
parser = argparse.ArgumentParser(
    description='Script for merging CSV files with students results.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--results_csv',
    required=True,
    help="path of the CSV file created from my numbers spreadsheet, which contains the results.",
    type=str,
)
parser.add_argument(
    '--moodle_csv',
    required=True,
    help="path of the CSV file downloaded from Moodle, in which the results should be added.",
    type=str,
)
args = parser.parse_args()


def main():
    # read results csv
    results_csv = Path(args.results_csv)
    if not results_csv.exists():
        raise RuntimeError("Invalid `results_csv` given.")
    results_df = pd.read_csv(
        results_csv, 
        sep=';', 
        header=[0,1], 
        skipfooter=2,
        decimal=',',
        na_values='-',
        engine='python',)

    # read moodle csv
    moodle_csv = Path(args.moodle_csv)
    if not moodle_csv.exists():
        raise RuntimeError("Invalid `results_csv` given.")
    moodle_df = pd.read_csv(
        moodle_csv, 
        sep=',', 
        decimal=',',
        na_values='-',
        engine='python',)

    # rename unnamed columns
    results_df = rename_unnamed(results_df)

    # keep only Matrikelnummer and points, drop rest
    results_df = results_df[[('Matrikelnummer',''),('3','∑')]]
    results_df = results_df.droplevel(1, axis=1)
    results_df = results_df.rename(columns={'3':'Bewertung'})

    # merge columns
    merged = moodle_df.join(results_df.set_index('Matrikelnummer'), on='key')
    merged = moodle_df.merge(
        results_df, 
        how='left', on='Matrikelnummer',
        )

    # write output csv
    with open(Path() / 'out.csv', mode='w') as f:
        merged.to_csv(
            f, 
            sep=',',
            decimal=',',
            index=False)
    

if __name__ == '__main__':
    # license
    print(dedent("""
    send_results.py  Copyright (C) 2021  Paul Orschau
    This program comes with ABSOLUTELY NO WARRANTY; for details see `LICENSE` file.
    This is free software, and you are welcome to redistribute it
    under certain conditions; for details see `LICENSE` file.
    """))

    main()



