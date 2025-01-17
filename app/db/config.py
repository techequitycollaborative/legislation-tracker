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
#from configparser import ConfigParser


#def config(section, filename='db/credentials.ini'):
#    # create a parser
#    parser = ConfigParser()
#    # read config file
#    parser.read(filename)

#    # get section, default to postgresql
#    values = {}
#    if parser.has_section(section):
#        params = parser.items(section)
#        for param in params:
#            values[param[0]] = param[1]
#    else:
#        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

#    return values


import os
from configparser import ConfigParser

def config(section):
    # First, try to get configuration from Digitial Ocean environment variables
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'sslmode': os.getenv('SSL_MODE')
    }

    # Check if environment variables are empty
    if all(value is None for value in db_config.values()):
        # If environment variables are not set, fall back to the credentials.ini file
        filename = 'db/credentials.ini'
        parser = ConfigParser()
        if parser.read(filename):
            if parser.has_section(section):
                db_config = {
                    'host': parser.get(section, 'host'),
                    'port': parser.get(section, 'port'),
                    'dbname': parser.get(section, 'database'),
                    'user': parser.get(section, 'user'),
                    'password': parser.get(section, 'password'),
                    'sslmode': parser.get(section, 'sslmode')
                }
            else:
                raise Exception(f"Section {section} not found in the {filename} file")
        else:
            raise Exception(f"Could not read {filename} file")

    return db_config
