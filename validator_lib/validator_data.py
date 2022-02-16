import platform
import os
from appdirs import AppDirs

DOCS_URL = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/README.md'
ERROR_GLOSSARY_URL = 'https://github.com/Center-for-Research-Libraries/validator/blob/main/docs/disqualifying_issues.md'

CURRENT_OS = platform.system()
HOME_FOLDER = os.path.expanduser("~")
CRL_FOLDER = os.path.join(os.path.expanduser("~"), 'CRL')
MARC_DB_NAME = 'marc_collection.db'
ISSN_DB_NAME = 'ISSN_db.db'
API_KEY_CONFIG_NAME = 'api_keys.ini'
APPDIRS_DIRECTORY = AppDirs(appname='CRL').user_data_dir

VALIDATOR_INPUT_FOLDER = os.path.join(os.getcwd(), 'input')
VALIDATOR_OUTPUT_FOLDER = os.path.join(os.getcwd(), 'output')
VALIDATOR_DATA_FOLDER = os.path.join(os.getcwd(), 'data')
VALIDATOR_LOGS_FOLDER = os.path.join(os.getcwd(), 'logs')
