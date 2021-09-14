# Instructions

### Install Python

Download the most recent version of Python 3 from [python.org](https://www.python.org/downloads/) and install it. Be sure to click the checkbox for adding Python to your PATH.

### Install additional requirements and create data folders

Open a command line window in the PAPR validation folder. The easiest way to do this is to open the folder in Windows Explorer then type `cmd` in the address bar. 

Install needed additional Python libraries with this command: `pip install -r requirements.txt`.

The system might give you a warning that says you need to upgrade pip. This can be ignored. Note that for Linux and MacOS you may need to replace `python` with `python3` for all commands.

### ISSN Database

The project can use but does not require access to a copy of the ISSN database. If you are running the project from a machine on CRL's internal network and have the Tech Services drive mapped, the program should be able to scan your drives and find the database there. Otherwise, contact Nate to get a copy. Users outside of CRL will need a separate license from the ISSN International Centre to use the ISSN database.

### Add input files

Put your input files in the input folder. They should all go in the top level folder, not in any subfolders.

Input files can be MARC text (.mrk), Excel, csv, or tsv (with a ".tsv" or ".txt" extension).

### Add a JSTOR file, if needed

NOTE: The JSTOR section isn't implemented, so ignore the below.

If you want the system to check whether or not a title is in JSTOR, add a file of JSTOR ISSNs to the data folder. The file should be a text list of only jstor ISSNs, and should have a name starting with "jstor" and ending with ".txt". It doesn't have to be called `jstor.txt`, but that would be an obvious option.

### Other notes

The Validator uses general data files in a folder called `CRL MARC Machine` located in the user's home directory. If you have used the CRL MARC Machine on this computer then the directory likely already exists. If not the system will create it.

## Running the Validator

The validator can be run by typing `python papr_validator.py` in the command window. You may see a warning that says "Using slow pure-python SequenceMatcher. Install python-Levenshtein to remove this warning." This can be ignored.

From here, running the Validator should be relatively straightforward.

### Set up your WorldCat Search API keys

If you have used the CRL MARC Machine on this computer you might be able to skip this step. Otherwise, choose this option and enter a valid API key and a name for it.

Choosing this option will cause a separate window to open. It might open under the command line window, so look for it on your taskbar if you don't see it. 

### Do a quick scan of any MARC input files

This runs through all of the MARC files in the input folder to check for common fields. It will print a report in a file called `Quick Scan.txt` that will go in the top level folder. This is intended to help you figure out what fields contain holdings, bib IDs, and so forth, and can be skipped if you are already familiar with your MARC input files.

This option won't appear if there are no MARC files in the input folder.

### Specify fields in input files

Before you can analyze a file you have to tell the system what fields (for MARC records) or columns (for xlsx, csv, and tsv) contain relevant fields.

Choosing this option will cause a separate window to open. It might open under the command line window, so look for it on your taskbar if you don't see it.

MARC fields and subfields should be entered like "035a". Spreadsheet columns should be entered as numbers, with 1 as the first column.

Skip any fields that aren't in the input file.

This must be done before moving on to the next steps.

###  Process input and WorldCat MARC to create outputs

This runs the Validator proper. The script will ask if you want to delete any files that are in your output folder. If you don't do so, the the Validator will add a number to the name of new files it creates. So if you already have `CRL checklist.xlsx`, it will add `CRL checklist(1).xlsx`.

The Validator will run and produce two spreadsheets for every institution, that will go in the `output` directory. In addition, if a MARC file has any validation errors the Validator will produce a text file detailing them.

While the Validator is running, the process will download MARC records from the WorldCat API for any OCLC number that it has not updated in the last year. This means that initial runs of a set of data can be *much* longer than later runs. The speed of the API work will depend heavily on network conditions, both locally and at OCLC.
