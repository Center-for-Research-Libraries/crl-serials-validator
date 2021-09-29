import os
import yaml


from validator_lib.validator_config import ValidatorConfig
from validator_lib.validator_file_locations import ValidatorFileLocations
from validator_lib.bulk_validator_preferences import BulkConfig


class HeadlessPrep:
    """
    Class to read bulk field and issue data, put it in the regular Validator's configuration file, then run the input
    files one at a time.
    """

    def __init__(self):
        self.file_locations = ValidatorFileLocations()
        self.validator_config = ValidatorConfig()
        self.bulk_config = BulkConfig()

        self.check_input_fields()

    def check_input_fields(self):
        for input_file in self.file_locations.input_files:
            print(input_file)
            input_fields = self.validator_config.get_input_fields(input_file)
            if input_fields:
                continue
            input_file_start = input_file.split('.')[0].lower()
            program = None
            if input_file_start in self.bulk_config.config_data:
                program = input_file_start
            elif input_file_start in self.bulk_config.associated_names_map:
                program = self.bulk_config.associated_names_map[input_file_start]
            if not program:
                continue

            # input_fields = self.
