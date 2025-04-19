Streaming Data Processing for Dashboard

This project runs a Python script that processes transportation and environmental data and stores the results in a PostgreSQL database hosted on Google Cloud SQL. The script runs automatically every 15 minutes using GitHub Actions.

How It Works

The script loads data from the CSV file athens_routes.csv

It connects to the database using a secure Cloud SQL Proxy

A GitHub Actions workflow triggers the script every 15 minutes

GitHub Secrets are used to manage credentials securely

Technologies Used

Python 3.10

PostgreSQL on Google Cloud SQL

Cloud SQL Proxy

GitHub Actions

GitHub Secrets

GitHub Secrets Required

API_KEY: external API key (optional, for any APIs used)

DATABASE_URL: connection string to the PostgreSQL database

GCP_CREDENTIALS: JSON key for Google Cloud service account

Security Features

No credentials are exposed in code

.gitignore is configured to protect sensitive files

Cloud SQL access is restricted to IAM-based service account authentication

Public IP access is disabled

Main Files

main.py: the data processing and insertion script

athens_routes.csv: input data file with route information

requirements.txt: Python dependencies

.github/workflows/: contains GitHub Actions workflow configuration

Author

Developed by Eleftherios Varv
