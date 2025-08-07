#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py

Configuration script for PosgreSQL database connection. 
    - Loads database credentials from Digital Ocean environmental variables if deployed on digital ocean servor
    - If deployed locally, loads database credentials from locally configured credentials.ini file at: root/app/db/credentials.ini

Used to power query.py in order to pull data from PostgreSQL database into Streamlit app for further manipulation in Python.

Date: Jan 15, 2025
"""

import os
from configparser import ConfigParser

def config(section, filename = 'db/credentials.ini'):
    '''
    Params: section string (i.e. 'postgres')
    Returns: database credentials as string values, to be used as inputs to query function in query.py
    '''
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
        parser = ConfigParser()
        if parser.read(filename):
            if parser.has_section(section):
                db_config = {
                    'host': parser.get(section, 'host'),
                    'port': parser.get(section, 'port'),
                    'dbname': parser.get(section, 'dbname'),
                    'user': parser.get(section, 'user'),
                    'password': parser.get(section, 'password'),
                    'sslmode': parser.get(section, 'sslmode')
                }
            else:
                raise Exception(f"Section {section} not found in the {filename} file")
        else:
            raise Exception(f"Could not read {filename} file")

    return db_config
