#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auth.py
February 2025
@author: danyasherbini

This script locates and fetches Google credentials from a remote server, which are used to build the Google
authentication mechanism for the legislation tracker app. The server is accessed via SSH with the paramiko library.

A private OPENSSH key is required in order to access the droplet.
"""

import os
import io
import paramiko
import platform

def fetch_google_credentials_from_droplet():
    """
    Fetches Google credentials file from the remote server via SSH.

    Parameters: None
    Outputs: Local path to google credentials file, used to build Google authenticator widget.
    """

    # Detect if running locally (Mac/Linux)
    is_local = os.getenv("ENV") == "local" or platform.system() in ["Darwin", "Linux"]

    # If running locally, then get ssh key from local file
    if is_local:
        private_key_path = os.path.expanduser("~/.ssh/id_rsa") #  replace path to local ssh key as needed
        
        if not os.path.exists(private_key_path):
            raise ValueError(f"Local private key not found at {private_key_path}. "
                             f"Ensure you have SSH access set up.")

        try:
            key = paramiko.RSAKey.from_private_key_file(private_key_path)
        except Exception as e:
            raise ValueError(f"Error loading local SSH key: {e}")

    # Or if running on remote server, get ssh key from remote environment 
    else:
        private_key = os.getenv("PRIVATE_SSH_KEY")
        if not private_key:
            raise ValueError("PRIVATE_SSH_KEY is empty or not set.")
        
        private_key_file = io.StringIO(private_key)
        
        try:
            key = paramiko.PKey.from_private_key(private_key_file)
        except Exception as e:
            raise ValueError(f"Error loading SSH private key: {e}")

    # Set up SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect('143.198.149.149', port=6022, username='root', pkey=key)
    except Exception as e:
        raise ValueError(f"SSH connection failed: {e}")

    # Fetch the credentials file from server
    sftp = ssh.open_sftp()
    local_path = './google_credentials.json'
    sftp.get('/root/auth/google_credentials.json', local_path) # save it locally
    sftp.close()
    ssh.close()

    return local_path

