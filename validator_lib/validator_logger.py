import logging
import os
import datetime

from validator_lib.utilities import get_directory_location


DEBUG_MODE = False


def set_validator_logger(log_to_screen=True):
    log_directory = get_directory_location('logs')
    log_file_name = 'validator_log_{:%Y-%m-%d}.log'.format(datetime.datetime.now())
    log_file = os.path.join(log_directory, log_file_name)

    # if DEBUG_MODE is set to True we will automatically log to the screen
    if DEBUG_MODE is True:
        logging.basicConfig(level=logging.DEBUG, 
                            format="%(asctime)s [%(levelname)s] %(message)s", 
                            datefmt="%Y-%m-%d %H:%M:%S",
                            handlers=[
                                logging.FileHandler(log_file_name),
                                logging.StreamHandler()
                            ]
        )        
    elif log_to_screen is True:
        logging.basicConfig(level=logging.INFO, 
                            format="%(asctime)s [%(levelname)s] %(message)s", 
                            datefmt="%Y-%m-%d %H:%M:%S",
                            handlers=[
                                logging.FileHandler(log_file),
                                logging.StreamHandler()
                            ]
        )
    else:
        logging.basicConfig(
            format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO, filename=log_file)
