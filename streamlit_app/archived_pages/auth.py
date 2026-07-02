#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auth.py
February 2025

This script locates and fetches Google credentials from a remote server, which are used to build the Google
authentication mechanism for the legislation tracker app. The server is accessed via SSH with the paramiko library.

A private OPENSSH key is required in order to access the droplet.
"""

import os
import io
import paramiko
from dotenv import load_dotenv


def fetch_google_credentials_from_droplet():
    """
    Fetches Google credentials file from the remote server via SSH.

    - If running locally (with or without Docker), uses ~/.ssh/id_rsa.
    - If running on DigitalOcean, uses PRIVATE_SSH_KEY from App Platform environment variables.

    Returns:
        str: Local path to the Google credentials file.
    """
   
    # Load .env file only if ENV is not already set
    if not os.getenv("ENV"):
        load_dotenv()

    # Default to "production" unless explicitly set
    ENV = os.getenv("ENV", "production")  
    local_key_path = os.path.expanduser("~/.ssh/id_rsa")  # Local SSH key file path (change path as needed)

    # Define key variable
    key = None  

    if ENV == "local" or ENV == "development":
        print(f"Running locally - Using SSH key file at {local_key_path}.")
        
        if not os.path.exists(local_key_path):
            raise ValueError(f"Error: Local private key not found at {local_key_path}. "
                             f"Ensure you have SSH access set up.")

        try:
            key = paramiko.RSAKey.from_private_key_file(local_key_path)
        except Exception as e:
            raise ValueError(f"Error loading local SSH key: {e}")

    else:  # Assume the app is running on DigitalOcean server production environment
        print("Running on DigitalOcean - Using PRIVATE_SSH_KEY from environment.")

        private_key = os.getenv("PRIVATE_SSH_KEY")
        if not private_key:
            raise ValueError("Error: PRIVATE_SSH_KEY is not set in the environment.")

        private_key_file = io.StringIO(private_key)

        try:
            key = paramiko.RSAKey.from_private_key(private_key_file)
        except Exception as e:
            raise ValueError(f"Error loading SSH private key from environment: {e}")

    # Connect to server via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect('143.198.149.149', port=6022, username='root', pkey=key)
    except Exception as e:
        raise ValueError(f"Error: SSH connection failed: {e}")

    # Fetch the Google credentials file from the server
    sftp = ssh.open_sftp()
    local_path = './google_credentials.json'
    sftp.get('/root/auth/google_credentials.json', local_path)  # Save it locally
    sftp.close()
    ssh.close()

    return local_path

