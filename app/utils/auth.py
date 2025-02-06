import paramiko
import os
import io

def fetch_google_credentials_from_droplet():
    # Load private key from environment variable
    private_key = os.getenv("PRIVATE_SSH_KEY")

    # Convert the string to a file-like object
    private_key_file = io.StringIO(private_key)  # Use StringIO for string input

    # Initialize the SSH client and load the private key
    key = paramiko.RSAKey.from_private_key(private_key_file)

    # Set up SSH connection to your Droplet
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to Droplet on port 6022 (adjust if necessary)
    ssh.connect('143.198.149.149', port=6022, username='root', pkey=key)

    # Use SFTP to fetch the google_credentials.json from Droplet
    sftp = ssh.open_sftp()
    local_path = './google_credentials.json'  # Save file locally
    sftp.get('/root/auth/google_credentials.json', local_path)
    sftp.close()
    ssh.close()
    return local_path