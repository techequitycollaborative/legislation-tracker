#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py

Configuration script for PosgreSQL database connection. Runs credentials.ini file to connect to database.

Date: Jan 15, 2025

---
Input: section string, credentials.ini
Output: string values
"""
from configparser import ConfigParser


def config(section, filename='db/credentials.ini'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    values = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            values[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return values
