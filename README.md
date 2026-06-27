# ETL Pipeline - Sales Data

An automated ETL pipeline that extracts sales data from CSV, cleans it, validates it, and loads it into CockroachDB.

## Features
- Extract: Read raw CSV data
- Transform: Clean phone numbers, standardize dates, handle missing values
- Validate: Remove invalid records
- Load: Insert clean data into CockroachDB
- Orchestration: Dedicated OOP ETL engine coordinates the full pipeline

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
DB_PASSWORD=your_real_password
DB_SSL_ROOT_CERT=C:/Users/<YOUR_USER>/AppData/Roaming/postgresql/root.crt
LOAD_MODE=skip
```

`LOAD_MODE` options:
- `skip` (default): insert new rows, skip duplicates by `sale_id`
- `upsert`: insert new rows and update existing rows by `sale_id`

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

The pipeline now prints a load summary with attempted rows, inserted/affected rows, skipped rows (in `skip` mode), and total rows currently in `sales_clean`.

## Deep Implementation Coverage

### 1) Automated Data Ingestion & ETL Engine
- Ingestion is automated from CSV source with reusable extractor classes.
- ETL orchestration is centralized in `engine/etl_engine.py` (`ETLEngine` class).
- Pipeline execution is deterministic and repeatable across runs.

### 2) Python Server-Side Pipeline Components
- Core pipeline modules are written in Python with clean class boundaries:
	- Extractors (`extractors/`)
	- Transformers (`transformers/`)
	- Loaders (`loaders/`)
	- Engine (`engine/`)
- CLI and web UI both use the same backend ETL components.

### 3) OOP and Maintainable Design
- Abstract base classes enforce contracts for extractors/loaders.
- `ETLEngine` composes extractor/cleaner/validator/loader for separation of concerns.
- `models/pipeline_report.py` uses dataclasses for structured reporting.

### 4) Efficient SQL + Safe Relational Storage
- Parameterized SQL statements are used for write operations.
- Transaction handling includes commit on success and rollback on failure.
- Conflict-safe loading is configurable via `LOAD_MODE`:
	- `skip` (idempotent insert)
	- `upsert` (insert/update by `sale_id`)

### 5) Git & GitHub Workflow
- Branching and contribution standards are defined in `CONTRIBUTING.md`.
- Recommended branch naming:
	- `feature/<name>`
	- `fix/<name>`
	- `docs/<name>`
- Use Pull Requests for review before merging to `main`.

### 6) System Documentation
- `README.md` covers setup, runtime, DB connection, and UI usage.
- `CONTRIBUTING.md` documents team workflow and quality standards.
- Module-level docstrings and method docstrings describe execution logic.

## Run UI

```bash
python ui_app.py
```

Then open: `http://127.0.0.1:5000`

The UI is fully wired to pipeline features:
- Initialize CockroachDB table (`sales_clean`)
- Upload custom CSV or use `data/sales.csv`
- Select load mode (`skip` or `upsert`)
- Run full ETL flow from the browser
- View raw, cleaned, and validated data previews
- View load summary and table row counts
- Explore latest records from CockroachDB (`sales_clean`)