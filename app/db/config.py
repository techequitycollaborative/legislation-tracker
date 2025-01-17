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


from configparser import ConfigParser
import os

def config(section='postgres'):
    if os.getenv('DIGITALOCEAN_ENV', False):  # Check if running in DigitalOcean; if so, load credentials from digitial ocean environmental variables
        return {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'sslmode': os.getenv('SSL_MODE')
        }
    else:  # Load from credentials.ini for local development
        parser = ConfigParser()
        filename = 'db/credentials.ini'
        parser.read(filename)
        if parser.has_section(section):
            return {key: val for key, val in parser.items(section)}
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
