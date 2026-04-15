"""
Input: section string, credentials.ini
Output: string values

Given a section string (ex: postgres), return parameters
"""

import os
from configparser import ConfigParser
from pathlib import Path


def config(section, filename=None):
    # First, try to get configuration from Digitial Ocean environment variables
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "sslmode": os.getenv("SSL_MODE"),
    }

    if all(value is not None for value in db_config.values()):
        return db_config  # early return when env vars are present

    if filename is None:
        filename = Path(__file__).resolve().parent / "credentials.ini"

    if all(value is None for value in db_config.values()):
        print(f"=== ENV VARS ARE NONE, FALLING BACK TO {filename} ===")

    parser = ConfigParser()
    parser.read(filename)

    values = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            values[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )

    return values
