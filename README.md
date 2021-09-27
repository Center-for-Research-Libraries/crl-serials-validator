# The CRL Serials Validator
Validate serials bibliographic and holdings data according to a set of user-defined rules. 

## About

The CRL Serials Validator was originally built at the Center for Research Libraries to aid in data analysis for shared print projects, specifically for the PAPR project at CRL It howver can be useful whenever you need to check and verify the quality of any set of serials bibliographic and holdings data.

The CRL Serials Validator works by reading user-supplied input data and comparing it against bibliographic data downloaded from the WorldCat Search API. It then checks every title in the input data according to rules that can mostly be turned on or off by the user. Typically the CRL Serials Validator looks for titles that exist in WorldCat, that are hard copy serials, that have titles roughly matching that on the WorldCat record, that have holdings with dates matching the publication dates as listed in the WorldCat MARC, and that (when appropriate) have valid and legitimate ISSNs.

If the user has a subscription to data downloads from the ISSN Centre, the user can additionally validate their data against this ISSN data.

## Basic Requirements

To install and use the CRL Serials Validator you will need:

* One or more [WorldCat Search API keys](https://help.oclc.org/Discovery_and_Reference/WorldCat_Discovery/Troubleshooting/How_do_I_request_a_WSKey_for_the_WorldCat_Search_API?sl=en).
* Python (version 3.4 or later), with the ability to install extra Python libraries.
* Input files in one of the following formats: xlsx, csv, tab-separated text, or MARC text (mrk).

The CRL Serials Validator has been tested and used on Windows 10 and Linux (Ubuntu 20.04). It should also work on Mac OS, but hasn't been tested.

## Quick Start

1. Install Python 3. Add Python to your PATH.
2. Type `pip install -r requirements.txt` to install the needed Python libraries.
3. Put your input files in the `input` folder.
4. Add the ISSN database (optional, if you have a subscription to it).
5. Run the CRL Serials Validator with `python crl_serials_validator.py`.
6. Setup your API keys.
7. Tell the scripts what input fields your input files have.
8. Validate the input data.

## Complete Instructions

### Install Python

Download the most recent version of Python 3 from [python.org](https://www.python.org/downloads/) and install it. Be sure to click the checkbox for adding Python to your PATH.

### Install additional requirements and create data folders

Open a command line window in the CRL Serials Validator folder. The easiest way to do this is to open the folder in Windows Explorer then type `cmd` in the address bar. 

Install needed additional Python libraries with this command: `pip install -r requirements.txt`.

The system might give you a warning that says you need to upgrade pip. This can be ignored. Note that for Linux and MacOS you may need to replace `python` with `python3` for all commands.

### ISSN Database

The project can use but does not require access to a copy of the ISSN database. If you are running the project from a machine on CRL's internal network and have the Tech Services drive mapped, the program should be able to scan your drives and find the database there. Otherwise, contact Nate to get a copy. Users outside of CRL will need a separate license from the ISSN International Centre to use ISSN data.

### Add input files

Put your input files in the input folder. They should all go in the top level folder, not in any subfolders.

Input files can be MARC text (.mrk), Excel, csv, or tsv (with a ".tsv" or ".txt" extension).

### Add a JSTOR file, if needed

If you want the system to check whether or not a title is in JSTOR, add a file of JSTOR ISSNs to the data folder. The file should be a text list of only jstor ISSNs, and should have a name starting with "jstor" and ending with ".txt". It doesn't have to be called `jstor.txt`, but that would be an obvious option.

### Data files

Beside its regular output files the Validator will create a file called `marc_database.db` (for storing downloaded MARC files), a file called `api_keys.ini` (to store WorldCat Search API keys), and a general configuration file called `validator_config.ini`. Usually these files will all be found in the `data` directory in the CRL Serials Validator folder. If however you have an old copy of the Validator or have used the CRL MARC Machine program then some or all of them may be found in the  `CRL MARC Machine` folder in your home directory.

If you hae a copy of the ISSN database, it should be put in the same directory that contains `marc_database.db`.

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

