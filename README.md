# Validator
Validate serials bibliographic and holdings data according to a set of user-defined rules. 

## About

The Validator was built to aid in data analysis for shared print projects, specifically for the PAPR project at the Center for Research Libraries. It howver can be useful whenever you need to check and verify the quality of any set of serials bibliographic and holdings data.

The Validator works by reading user-supplied input data and comparing it against bibliographic data downloaded from the WorldCat Search API. It then checks every title in the input data according to rules that can mostly be turned on or off by the user. Typically the Validator looks for titles that exist in WorldCat, that are hard copy serials, that have titles roughly matching that on the WorldCat record, that have holdings with dates matching the publication dates as listed in the WorldCat MARC, and that (when appropriate) have valid and legitimate ISSNs.

If the user has a subscription to data downloads from the ISSN Centre, the user can additionally validate their data against this ISSN data.

## Basic Requirements

To install and use the Validator you will need:

* One or more WorldCat Search API keys.
* Python (version 3.4 or later), with the ability to install extra Python libraries.
* Input files in one of the following formats: xlsx, csv, tab-separated text, or MARC text (mrk).

The Validator has been tested and used on Windows 10 and Linux (Ubuntu 20.04). It should also work on Mac OS, but hasn't been tested.

## Quick Start

1. Install Python 3. Add Python to your PATH.
2. Type `pip install -r requirements.txt` to install the needed Python libraries.
3. Put your input files in the `input` folder.
4. Add the ISSN database (optional, if you have a subscription to it).
5. Run the Validator with `python validator.py`.
6. Setup your API keys.
7. Tell the scripts what input fields your input files have.
8. Validate the input data.

For further information, see the [Validator Wiki](https://github.com/Center-for-Research-Libraries/validator/wiki).
