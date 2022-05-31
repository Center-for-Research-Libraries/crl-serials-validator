import os
import datetime


DOCS_URL = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/README.md'
ERROR_GLOSSARY_URL = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md'

CRL_FOLDER = os.path.join(os.path.expanduser("~"), 'CRL')

VALIDATOR_INPUT_FOLDER = os.path.join(os.getcwd(), 'input')
VALIDATOR_OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
VALIDATOR_DATA_FOLDER = os.path.join(os.getcwd(), 'data')
VALIDATOR_LOGS_FOLDER = os.path.join(os.getcwd(), 'logs')

MARC_DB_NAME = 'marc_collection.db'
ISSN_DB_NAME = 'ISSN_db.db'
API_KEY_CONFIG_NAME = 'api_keys.ini'
LOG_FILE_NAME = 'validator_log_{:%Y-%m-%d}.log'.format(datetime.datetime.now())

MARC_DB_LOCATION = os.path.join(CRL_FOLDER, MARC_DB_NAME)
API_KEY_CONFIG_LOCATION = os.path.join(CRL_FOLDER, API_KEY_CONFIG_NAME)
LOG_FILE_LOCATION = os.path.join(VALIDATOR_LOGS_FOLDER, LOG_FILE_NAME)

# Check if ISSN db is installed locally
if os.path.isfile(os.path.join(CRL_FOLDER, ISSN_DB_NAME)):
    ISSN_DB_LOCATION = os.path.join(CRL_FOLDER, ISSN_DB_NAME)
else:
    ISSN_DB_LOCATION = None