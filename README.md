# ETL Pipeline - Sales Data

An automated ETL pipeline that extracts sales data from CSV, cleans it, validates it, and loads it into CockroachDB.

## Features
- Extract: Read raw CSV data
- Transform: Clean phone numbers, standardize dates, handle missing values
- Validate: Remove invalid records
- Load: Insert clean data into CockroachDB

## Tech Stack
- Python 3.x
- CockroachDB (PostgreSQL wire protocol)
- Pandas
- Git & GitHub

## Setup

1. Create virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create or update `.env` with connection settings:

```env
DB_URL=postgresql://priyanshu:<PASSWORD-HIDDEN>@oldest-rat-17526.jxf.gcp-asia-south1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
DB_SSL_ROOT_CERT=C:/Users/<YOUR_USER>/AppData/Roaming/postgresql/root.crt
```

## Connect to oldest-rat

### Connection string
- SQL user: `priyanshu`
- Database: `defaultdb`
- Option/language: General connection string

Connection string:

```text
postgresql://priyanshu:<PASSWORD-HIDDEN>@oldest-rat-17526.jxf.gcp-asia-south1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
```

### Model Context Protocol (MCP)
Use the cluster connection instructions in Cockroach Cloud when configuring MCP-backed tools. You can always find these by selecting **Connect** on the cluster overview page.

Reference: https://www.cockroachlabs.com/docs/stable/connect-to-the-database.html

### Download CA cert (Windows, required once)
Run this in PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$env:appdata\postgresql" | Out-Null
Invoke-WebRequest -Uri "https://cockroachlabs.cloud/clusters/459408cf-74b3-46e9-8b49-99b7788f3fec/cert" -OutFile "$env:appdata\postgresql\root.crt"
```

Learn more about CA certs: https://www.cockroachlabs.com/docs/cockroachcloud/authentication#node-identity-verification

## Initialize schema

```bash
python setup_db.py
```

## Run pipeline

```bash
python pipeline.py
```