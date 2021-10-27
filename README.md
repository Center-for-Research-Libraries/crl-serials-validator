# The CRL Serials Validator
Validate serials bibliographic and holdings data according to a set of user-defined rules. 

## About

The CRL Serials Validator takes serials bibliographic and holdings data, checks it against data downloaded from the WorldCat Search API, validates it based on rules set by the user, and declares each title valid (accurate and in scope) or invalid based on what it finds.

The CRL Serials Validator was originally built at the [Center for Research Libraries](https://www.crl.edu) for use with the [the Print Archives Preservation Registry (PAPR)](http://papr.crl.edu/), to aid in checking serials bibliographic data for accuracy and appropriate scope. It can be used for similar work with shared print data, or anywhere that you need to check a large amount of serials data for accuracy and relevance.

Generally, the CRL Serials Validator attempts to answer these questions:

* Can the title be found in WorldCat?
* Is the title a serial?
* Is it attached to a hard copy bibliographic record?
* Do the holdings fit within the title's publication range?

Specific criteria can be set by the user, to make checking more or less strict as required.

The program can provess input data in a variety of formats: MARC, tab-separated and comma-separated text files, and Excel (xlsx) spreadsheets. It produces an output spreadsheet with information about every title in the input set, any relevant errors found, and a list of titles that passed all of the selected checks.

If the user has a subscription to data downloads from the ISSN Centre, the user can additionally validate their data against this ISSN data.

## Basic Requirements

To install and use the CRL Serials Validator you will need:

* One or more [WorldCat Search API keys](https://help.oclc.org/Discovery_and_Reference/WorldCat_Discovery/Troubleshooting/How_do_I_request_a_WSKey_for_the_WorldCat_Search_API?sl=en).
* Python (version 3.4 or later), with the ability to install extra Python libraries.
* Input files in one of the following formats: xlsx, csv, tab-separated text, or MARC text (mrk).

The CRL Serials Validator has been tested and used on Windows 10 and Linux (Ubuntu 20.04). It should also work on Mac OS, but hasn't been tested.

## Quick Start

1. Install Python 3. Add Python to your PATH.
2. Install the needed Python dependencies by typing `pip install -r requirements.txt`.
3. Put your input files in the `input` folder.
4. Add the ISSN database (optional, if you have a subscription to it).
5. Run the CRL Serials Validator with `python crl_serials_validator.py`.
6. Setup your API keys.
7. Tell the scripts what input fields your input files have.
8. Validate the input data.

## More information

### Input files

Put your input files in the input folder. They should all go in the top level folder, not in any subfolders. Input files can be MARC text (.mrk), Excel, csv, or tsv (with a ".tsv" or ".txt" extension).

### Data files

Beside its regular output files the Validator will create a file called `marc_database.db` (for storing downloaded MARC files), a file called `api_keys.ini` (to store WorldCat Search API keys), and a general configuration file called `validator_config.ini`. The `validator_config.ini` will be put in the `data` folder in the CRL Serials Validator's main folder. The other two files will go in the user's data directory in a folder called `CRL`. On Windows this will usually be found at `'C:\Users\USERNAME\AppData\Local\CRL\CRL'. On most Linux systems it will usually be at `/home/USERNAME/.local/share/CRL`.

To create a "portable" version of the application, move the `marc_database.db` and `api_keys.ini` files to the `data` folder in the main application folder. After that the application will default to using those files and won't try to create files in other places on the user's drive.

If you hae a copy of the ISSN database, it should be put in the same directory that contains `marc_database.db`.

### JSTOR

If you want the system to check whether or not a title is in JSTOR, add a file of JSTOR ISSNs to the data folder. The file should be a text list of only jstor ISSNs, and should have a name starting with "jstor" and ending with ".txt". It doesn't have to be called `jstor.txt`, but that would be an obvious option.

### ISSN Database

The project can use, but does not require, data from the ISSN International Centre stored in an SQLite database. Users outside of CRL will need a separate license from the ISSN International Centre to use ISSN data. Tools for creating a database from raw ISSN MARC data will be included in a future version of the CRL Serials Validator. 

### Planned updates

* The next version of the CRL Serials Validator will have a full (non command line) GUI, and by default will run in graphical mode.
* We will have a binary (.exe file) release of the CRL Serials Validator for Windows, so it can be run by clicking an icon rather than opening a command line.

### Other documentation

* Glossaries of...
    - ...possible [disqualifying issues](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md).
    - ...terms from ["Originally from" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/originally_from.md).
    - ...terms from ["For review" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/for_review.md).
    - ...terms from the ["Checklist" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/checklist.md).
* How to run the CRL Serials Validator in [bulk/"headless" mode](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/bulk_mode.md).

## Running the CRL Serials Validator

The CRL Serials Validator can be run by typing `python crl_serials_validator.py` in the command window. You may see a warning that says "Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning." This can be ignored.

From here, running the CRL Serials Validator should be relatively straightforward.

### Set up your WorldCat Search API keys

If you have used the CRL MARC Machine on this computer you might be able to skip this step. Otherwise, choose this option and enter a valid API key and a name for it.

Choosing this option will cause a separate window to open. It might open under the command line window, so look for it on your taskbar if you don't see it. 

### Do a quick scan of any MARC input files

This runs through all of the MARC files in the input folder to check for common fields and print the results to the screen and the log file. This is intended to help you figure out what fields contain holdings, bib IDs, and so forth, and can be skipped if you are already familiar with your MARC input files.

This option won't appear if there are no MARC files in the input folder.

### Specify fields in input files

Before you can analyze a file you have to tell the system what fields (for MARC records) or columns (for xlsx, csv, and tsv) contain relevant fields.

Choosing this option will cause a separate window to open. It might open under the command line window, so look for it on your taskbar if you don't see it.

MARC fields and subfields should be entered like "035a". Spreadsheet columns should be entered as numbers, with 1 as the first column.

Skip any fields that aren't in the input file.

This must be done before moving on to the next steps.

### Specify disqualifying issues

Choose this option to determine what issues will cause the Validator to fail a specific title. The Validator will always check for every issue and report when it finds them, but will only fail titles on the issues you specify.

There is a [glossary of disqualifying issues](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md) in the documentation.

###  Process input and WorldCat MARC to create outputs

This runs the Validator proper. The script will ask if you want to delete any files that are in your output folder. If you don't do so, the the Validator will add a number to the name of new files it creates. So if you already have `CRL checklist.xlsx`, it will add `CRL checklist(1).xlsx`.

The Validator will run and produce two spreadsheets for every institution, that will go in the `output` directory. In addition, if a MARC file has any validation errors the Validator will produce a text file detailing them.

While the Validator is running, the process will download MARC records from the WorldCat API for any OCLC number that it has not updated in the last year. This means that initial runs of a set of data can be *much* longer than later runs. The speed of the API work will depend heavily on network conditions, both locally and at OCLC.

For more on the outputs, see the glossary of terms for the ["Originally from" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/originally_from.md), the ["For review" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/for_review.md), and the the ["Checklist" output worksheet](https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/checklist.md).

