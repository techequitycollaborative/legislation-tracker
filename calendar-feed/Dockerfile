# Build context must be the monorepo root so COPY db/ works:
#   docker compose -f calendar-feed/compose.yaml up --build

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY calendar-feed/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared db module from monorepo root
COPY db/ ./db/

# Copy service source
COPY calendar-feed/ ./

EXPOSE 5000

CMD ["gunicorn", "app:create_app()", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]