import paramiko
import os

# Set up SSH connection to your Droplet and retrieve the google_credentials.json file
def fetch_google_credentials_from_droplet():
    # Set up SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load private key from environment variables (or secrets manager)
    private_key = os.getenv("SSH_KEY")
    key = paramiko.RSAKey.from_private_key(private_key)

    # Connect to Droplet on port 6022 (adjust if necessary)
    ssh.connect('143.198.149.149', port=6022, username='root', pkey=key)

    # Use SFTP to fetch the google_credentials.json from Droplet
    sftp = ssh.open_sftp()
    local_path = './google_credentials.json'  # Save file locally
    sftp.get('root/auth/google_credentials.json', local_path)
    sftp.close()
    ssh.close()
    return local_path