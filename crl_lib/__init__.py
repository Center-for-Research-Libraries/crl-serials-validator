from pathlib import Path

"""
All data files (local databased for MARC and holders; API keys file) are stored in the CRL_FOLDER.

By default this is in a folder called "CRL" in the user's home directory.
Change the variable below to set a different default.
"""


CRL_FOLDER = Path.joinpath(Path.home(), "CRL")


def check_for_crl_directory() -> None:
    if not Path.is_dir(CRL_FOLDER):
        Path.mkdir(CRL_FOLDER)
