# moodle-tools

Tools for handling homework assignments downloaded from Moodle, more specifically the [Moodle instance](https://moodle.rwth-aachen.de) used by [RWTH Aachen](https://www.rwth-aachen.de/go/id/a/). May or may not work with other Moodle instances.

> This repo was created in 2021 for the lecture ["Mathematische Grundlagen II"](http://www.mathcces.rwth-aachen.de/3teaching/0classes/cesii), to more easily send corrected homework PDFs to students via email.


## Setup

Install all required dependencies with 
```
pip install -r requirements.txt
```


## Workflow

1. Use the "download all" option in Moodle to download all homework assignments in one folder (with subfolders per student).
2. Correct the homework submissions by directly manipulating the PDFs, e.g. using an iPad. Each subfolder should still only contain a single PDF file afterwards.
3. Add all the points for each student to the Numbers document (example provided in this repo).
4. Export the Numbers document as a CSV file.
5. Use `send_results.py` to send out the corrected PDFs to the students.
6. Enter all points manually in Moodle. (Maybe we will have a tool for this at some point too?)


## `send_results.py`

A simple script for sending out mass emails to students with corrected PDF assignments. Support for personalizing the email message, e.g. with scored points for that week's exercise.

Before using the script, please customize the parameters at the top of the script.

**Usage:**
```bash
python send_results.py --root_folder=/path/to/base/folder --results_csv=/path/to/csv --hw_index=1
```
To actually send the emails, disable debug mode with `--debug=False`. This is to avoid accidental spam.

To display a help message, use:
```bash
python send_results.py -h
```

The repo contains a sample Numbers document which has the correct format to be used with the script. Simply use that document and add students as rows, new results as columns. 

The student *groups* can potentially also change every week, but you only need to create a new `Gruppe` column if something actually changed that week. If a person used to belong to a group, but hasn't submitted anything this week, simply use a dash ('-'). 

For the script to work, e.g. the `Name` column entries need to have the exact same format as in Moodle (including special characters)!

Once you are done, export the file in Numbers as a CSV file. The example CSV file is also contained in the repo.