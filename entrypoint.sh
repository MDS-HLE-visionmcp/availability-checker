#!/bin/bash
set -e

# Initialize the database if needed
airflow db init

# Create admin user if it doesn't exist
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com || true

# Start the scheduler in the background
airflow scheduler &

# Start the webserver
exec airflow webserver --port 8080
