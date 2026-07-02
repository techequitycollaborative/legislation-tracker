# app/Dockerfile

# Set base image in Python
FROM python:3.12-slim-bookworm

# Set working directory to app folder in repo
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    #software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker's caching
COPY requirements.txt /app/

# Upgrade pip and install dependencies
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the Streamlit port
EXPOSE 8501

# Add a healthcheck for the container
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set the command to run Streamlit
CMD ["streamlit", "run", "/app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
