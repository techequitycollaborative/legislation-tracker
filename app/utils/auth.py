import paramiko
import os
import io

#def fetch_google_credentials_from_droplet():
    # Load private key from environment variable
#    private_key = os.getenv("PRIVATE_SSH_KEY")

    # Convert the string to a file-like object
#    private_key_file = io.StringIO(private_key)  # Use StringIO for string input

    # Initialize the SSH client and load the private key
#    key = paramiko.RSAKey.from_private_key(private_key_file)

    # Set up SSH connection to the droplet
#    ssh = paramiko.SSHClient()
#    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to droplet on port 6022
#    ssh.connect('143.198.149.149', port=6022, username='root', pkey=key)

    # Use SFTP to fetch the google_credentials.json from droplet
#    sftp = ssh.open_sftp()
#    local_path = './google_credentials.json'  # Save file locally
#    sftp.get('/root/auth/google_credentials.json', local_path)
#    sftp.close()
#    ssh.close()
#    return local_path


import os
import io
import paramiko
import platform

def fetch_google_credentials_from_droplet():
    """Fetch Google credentials from the remote server using SSH."""

    # Detect if running locally (Mac/Linux)
    is_local = os.getenv("ENV") == "local" or platform.system() in ["Darwin", "Linux"]

    if is_local:
        private_key_path = os.path.expanduser("~/.ssh/id_rsa")
        
        if not os.path.exists(private_key_path):
            raise ValueError(f"Local private key not found at {private_key_path}. "
                             f"Ensure you have SSH access set up.")

        try:
            key = paramiko.RSAKey.from_private_key_file(private_key_path)
        except Exception as e:
            raise ValueError(f"Error loading local SSH key: {e}")
    
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

    # Fetch the credentials file
    sftp = ssh.open_sftp()
    local_path = './google_credentials.json'
    sftp.get('/root/auth/google_credentials.json', local_path)
    sftp.close()
    ssh.close()

    return local_path

