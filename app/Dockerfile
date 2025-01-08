# app/Dockerfile

#Set base image in Python
FROM python:3.10-slim

# Set working directory to app folder in repo
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . /app/

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["streamlit", "run", "/app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]