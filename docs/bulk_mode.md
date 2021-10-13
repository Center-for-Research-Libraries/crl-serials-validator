# Bulk/"Headless" Mode

Bulk mode allows the user to run the CRL Serials Validator without human interaction. File fields and validations issues are set at the level of the program, with individual institutional record attached to the program. This allows the program to find required fields and issues automatically, so long as the input files are named appropriately.

## tl;dr

1. Set bulk options with `python crl_serials_validator.py -b`.
2. Run in bulk mode with `python crl_serials_validator.py -a`.

## Naming input files

Input file names should start with the name of a program or an institution, followed by a period and then any other data the user wants. Input file names are not case sensitive, so "MyProgram", "myprogram", and "MYPROGRAM" will all be interpreted as identical.

