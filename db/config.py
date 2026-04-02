"""
Input: section string, credentials.ini
Output: string values

Given a section string (ex: postgres), return parameters
"""

from configparser import ConfigParser
from pathlib import Path


def config(section, filename=None):
    if filename is None:
        filename = Path(__file__).resolve().parent / "credentials.ini"

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