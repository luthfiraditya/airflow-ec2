# Use an official Airflow image as a base
ARG AIRFLOW_VERSION=2.10.0
FROM apache/airflow:${AIRFLOW_VERSION}-python3.11

USER root

# Install system dependencies (if any)
# Example: RUN apt-get update && apt-get install -y --no-install-recommends <package-name> && apt-get clean && rm -rf /var/lib/apt/lists/*
# For this setup, common dependencies are often already in the base image.
# If you need specific database clients (e.g., for Oracle, SQL Server), install them here.
# RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && apt-get clean && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements first to leverage Docker cache
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy custom scripts
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]