"""
Basic interface for the CRL Serials Validator.

Usage:

    python crl_serials_validator.py  # run the Validator with a command-line interface
    python crl_serials_validator.py -a  # run the Validator in automated (headless) mode
    python crl_serials_validator.py --headless  # run the Validator in automated (headless) mode
    python crl_serials_validator.py -b  # set bulk/automated/headless mode preferences
    python crl_serials_validator.py --bulk_prefs  # set bulk/automated/headless mode preferences
    python crl_serials_validator.py -s  # set WorldCat Search API keys on the command line
    
"""

import sys
import os
import argparse
from termcolor import colored, cprint

from validator_lib.validator_controller import ValidatorController
from validator_lib.command_line_interface import SimpleValidatorInterface
from validator_lib.bulk_validator_preferences import run_bulk_config
import validator_lib.validator_file_locations


__version__ = '2025.6'


def parse_command_line_args():
    parser = argparse.ArgumentParser(
        description="Validate shared print holdings data.")
    parser.add_argument(
        "--headless", "-a", action="store_true", 
        help="Run in headless (automated) mode.")
    parser.add_argument(
        "--papr", "-p", action="store_true", 
        help="Create special output files for ingest into PAPR.")
    parser.add_argument(
        "--bulk_prefs", "-b", action="store_true", 
        help="Set bulk (headless) preferences.")
    parser.add_argument(
        "--file_locations", "-f", action="store_true", 
        help="Show the location of the application's data files.")
    args = parser.parse_args()
    return args


def headless_app():
    """
    Headless/bulk mode automatically starts processing input files, without 
    providing the opportunity to enter API keys, select issues, etc. Those 
    should be done either with the normal process or by setting them in bulk 
    using the bulk_prefs (b) option and the set_keys (s) option.
    """
    vc = ValidatorController(headless_mode=True)
    vc.run_checks_process()


def bulk_preferences():
    run_bulk_config()


if __name__ == "__main__":
    args = parse_command_line_args()        

    validator_lib.validator_file_locations.initialize_validator_folders()

    if args.file_locations is True:
        validator_lib.validator_file_locations.print_validator_file_locations()
        sys.exit()
    
    validator_lib.validator_file_locations.migrate_from_appdirs_directory()

    if args.bulk_prefs is True:
        bulk_preferences()
    elif args.headless is True:
        headless_app()
    else:
        SimpleValidatorInterface(args)
