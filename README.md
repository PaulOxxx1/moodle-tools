# moodle-mailer

Tools for handling homework assignments downloaded from Moodle.


## Setup

Install all required dependencies with 
```
pip install -r requirements.txt
```


## `send_results.py`

A simple script for sending out mass emails to students with corrected PDF assignments. Support for personalizing the email message, e.g. with scored points for that week's exercise.

Before using the script, please customize the parameters at the top of the script.

**Usage:**
```bash
python send_results.py --root_folder=/path/to/base/folder --results_csv=/path/to/csv --hw_index=1
```
To display a help message, use:
```bash
python send_results.py -h
```