from pathlib import Path
from datetime import datetime

import pandas as pd
import psycopg
from flask import Flask, request, render_template_string

from extractors.csv_extractor import CSVExtractor
from loaders.mysql_loader import MySQLLoader
from models.config import Config
from transformers.cleaner import DataCleaner
from transformers.validator import DataValidator

DEFAULT_CSV_PATH = "data/sales.csv"
UPLOADED_CSV_PATH = "data/uploaded_sales.csv"
REQUIRED_COLUMNS = {
    "sale_id",
    "date",
    "product_name",
    "quantity",
    "price_per_unit",
    "customer_phone",
}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

LAST_RESULTS = None
LAST_SOURCE_CSV = DEFAULT_CSV_PATH


def ensure_schema(config: Config) -> None:
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sales_clean (
                id INT PRIMARY KEY DEFAULT unique_rowid(),
                sale_id INT UNIQUE NOT NULL,
                sale_date DATE,
                product_name VARCHAR(100),
                quantity INT,
                price_per_unit DECIMAL(10,2),
                customer_phone VARCHAR(10)
        )
        """
        with psycopg.connect(config.db_url, **config.connection_options()) as conn:
                with conn.cursor() as cursor:
                        cursor.execute(create_table_sql)
                conn.commit()


def fetch_total_count(config: Config) -> int:
        with psycopg.connect(config.db_url, **config.connection_options()) as conn:
                with conn.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM sales_clean")
                        return int(cursor.fetchone()[0])


def fetch_table_data(config: Config, limit: int = 50) -> pd.DataFrame:
        query = """
        SELECT id, sale_id, sale_date, product_name, quantity, price_per_unit, customer_phone
        FROM sales_clean
        ORDER BY id DESC
        LIMIT %s
        """
        with psycopg.connect(config.db_url, **config.connection_options()) as conn:
                return pd.read_sql(query, conn, params=[limit])


def run_etl_flow(source_csv_path: str, selected_mode: str) -> dict:
        extractor = CSVExtractor(source_csv_path)
        cleaner = DataCleaner()
        validator = DataValidator()

        raw_df = extractor.extract()
    missing_cols = REQUIRED_COLUMNS.difference(set(raw_df.columns))
    if missing_cols:
        ordered = ", ".join(sorted(missing_cols))
        raise ValueError(f"Uploaded CSV missing required columns: {ordered}")

        cleaned_df = cleaner.clean_dataframe(raw_df.copy())
        valid_df = validator.validate(cleaned_df.copy())

        config = Config()
        config.load_mode = selected_mode
        config.validate()

        loader = MySQLLoader(config)
        load_summary = loader.load(valid_df)

        return {
                "raw": raw_df,
                "cleaned": cleaned_df,
                "valid": valid_df,
                "load_summary": load_summary,
        }


def df_to_html(df: pd.DataFrame, max_rows: int = 200) -> str:
        return df.head(max_rows).to_html(index=False, classes="data-table", border=0)


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ETL Control Deck</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --ink: #1f2933;
            --muted: #52606d;
            --surface: rgba(255, 255, 255, 0.85);
            --teal: #0f766e;
            --amber: #b45309;
            --line: rgba(31, 41, 51, 0.18);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: 'Space Grotesk', sans-serif;
            color: var(--ink);
            background: radial-gradient(circle at 0% 0%, #ffedd5 0%, #f8fafc 45%, #d1fae5 100%);
            min-height: 100vh;
            padding: 24px;
        }

        .wrap {
            max-width: 1300px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 18px;
        }

        .panel, .card {
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 16px;
            backdrop-filter: blur(5px);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        }

        .panel { padding: 16px; position: sticky; top: 16px; height: fit-content; }
        .card { padding: 16px; margin-bottom: 16px; }

        h1 { margin: 0 0 6px 0; font-size: clamp(1.4rem, 2.8vw, 2rem); }
        h2 { margin: 0 0 10px 0; font-size: 1.1rem; }
        h3 { margin: 0 0 8px 0; font-size: 1rem; }
        p, label, select, input, button { font-size: 0.95rem; }

        .subtitle { color: var(--muted); margin: 0 0 14px 0; }

        .metrics {
            display: grid;
            grid-template-columns: repeat(4, minmax(120px, 1fr));
            gap: 12px;
            margin-bottom: 16px;
        }

        .metric {
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 12px;
            background: rgba(255, 255, 255, 0.7);
            animation: fadeIn 280ms ease;
        }

        .metric .k { color: var(--muted); font-size: 0.82rem; }
        .metric .v { margin-top: 4px; font-size: 1.25rem; font-weight: 700; }

        form { display: grid; gap: 10px; }

        input[type="file"], select, input[type="number"] {
            width: 100%;
            padding: 8px 10px;
            border-radius: 10px;
            border: 1px solid var(--line);
            background: #fff;
            color: var(--ink);
        }

        .btn {
            padding: 10px 12px;
            border-radius: 10px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            transition: transform 120ms ease, box-shadow 120ms ease;
        }

        .btn:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(0,0,0,0.12); }

        .btn-primary { background: #0f766e; color: #fff; }
        .btn-secondary { background: #111827; color: #fff; }

        .status-ok, .status-warn, .status-err {
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 12px;
            border-left: 4px solid;
        }
        .status-ok { background: #ecfdf5; border-color: var(--teal); }
        .status-warn { background: #fffbeb; border-color: var(--amber); }
        .status-err { background: #fef2f2; border-color: #b91c1c; }

        .tables {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }

        .split {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
        }

        .table-wrap {
            overflow-x: auto;
            border: 1px solid var(--line);
            border-radius: 12px;
            background: #fff;
        }

        table.data-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.82rem;
        }

        table.data-table th, table.data-table td {
            border-bottom: 1px solid #e5e7eb;
            padding: 8px 10px;
            text-align: left;
            white-space: nowrap;
        }

        table.data-table th {
            background: #f8fafc;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(4px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 1024px) {
            .wrap { grid-template-columns: 1fr; }
            .panel { position: static; }
            .metrics { grid-template-columns: repeat(2, minmax(120px, 1fr)); }
            .split { grid-template-columns: 1fr; }
        }

        @media (max-width: 620px) {
            body { padding: 14px; }
            .metrics { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="wrap">
        <aside class="panel">
            <h2>Control Panel</h2>
            <p class="subtitle">Run ETL and inspect CockroachDB from one place.</p>

            <form method="post" enctype="multipart/form-data">
                <input type="hidden" name="action" value="run_pipeline" />
                <label>Load Mode</label>
                <select name="load_mode">
                    <option value="skip" {% if load_mode == 'skip' %}selected{% endif %}>skip</option>
                    <option value="upsert" {% if load_mode == 'upsert' %}selected{% endif %}>upsert</option>
                </select>

                <label>Upload CSV (optional)</label>
                <input type="file" name="csv_file" accept=".csv" />

                <button class="btn btn-primary" type="submit">Run Full Pipeline</button>
            </form>

            <form method="post" style="margin-top:10px;">
                <input type="hidden" name="action" value="init_db" />
                <input type="hidden" name="load_mode" value="{{ load_mode }}" />
                <button class="btn btn-secondary" type="submit">Initialize DB Table</button>
            </form>

            <p class="subtitle" style="margin-top:12px;">Source CSV: {{ source_csv }}</p>
        </aside>

        <main>
            <div class="card">
                <h1>ETL Control Deck</h1>
                <p class="subtitle">CSV -> Clean -> Validate -> CockroachDB</p>

                {% if status == 'ok' %}
                    <div class="status-ok">{{ message }}</div>
                {% elif status == 'warn' %}
                    <div class="status-warn">{{ message }}</div>
                {% elif status == 'err' %}
                    <div class="status-err">{{ message }}</div>
                {% endif %}

                <div class="metrics">
                    <div class="metric"><div class="k">DB Status</div><div class="v">{{ db_status }}</div></div>
                    <div class="metric"><div class="k">Rows in DB</div><div class="v">{{ db_rows }}</div></div>
                    <div class="metric"><div class="k">Rows in Source</div><div class="v">{{ source_rows }}</div></div>
                    <div class="metric"><div class="k">Active Load Mode</div><div class="v">{{ load_mode }}</div></div>
                </div>
            </div>

            <div class="card">
                <h2>Pipeline Output</h2>
                {% if results %}
                    <p><b>Raw rows:</b> {{ transform_summary.raw_rows }} | <b>Valid rows:</b> {{ transform_summary.valid_rows }} | <b>Removed rows:</b> {{ transform_summary.removed_rows }}</p>
                    <p>
                        <b>Mode:</b> {{ load_summary.mode }} |
                        <b>Attempted:</b> {{ load_summary.attempted }} |
                        {% if load_summary.mode == 'skip' %}
                            <b>Inserted:</b> {{ load_summary.affected }} |
                            <b>Skipped:</b> {{ load_summary.skipped }} |
                        {% else %}
                            <b>Affected:</b> {{ load_summary.affected }} |
                        {% endif %}
                        <b>Table rows:</b> {{ load_summary.total_rows }}
                    </p>
                {% else %}
                    <div class="status-warn">Run the pipeline to see transformation and load summaries here.</div>
                {% endif %}
            </div>

            <div class="card tables">
                <h2>Data Preview</h2>
                <h3>Source CSV</h3>
                <div class="table-wrap">{{ source_table|safe }}</div>

                {% if results %}
                    <div class="split">
                        <div>
                            <h3>Cleaned Data</h3>
                            <div class="table-wrap">{{ cleaned_table|safe }}</div>
                        </div>
                        <div>
                            <h3>Validated Data</h3>
                            <div class="table-wrap">{{ valid_table|safe }}</div>
                        </div>
                    </div>
                {% endif %}
            </div>

            <div class="card tables">
                <h2>Database Explorer</h2>
                <form method="post">
                    <input type="hidden" name="action" value="refresh_db" />
                    <input type="hidden" name="load_mode" value="{{ load_mode }}" />
                    <label>Rows to fetch</label>
                    <input type="number" name="db_limit" min="10" max="200" step="10" value="{{ db_limit }}" />
                    <button class="btn btn-secondary" type="submit">Refresh DB Data</button>
                </form>
                <div class="table-wrap" style="margin-top:10px;">{{ db_table|safe }}</div>
            </div>
        </main>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
        global LAST_RESULTS

        status = "warn"
        message = "Ready. Choose mode, optional CSV, then run full pipeline."
        load_mode = request.form.get("load_mode", "upsert").strip().lower() if request.method == "POST" else "upsert"
        db_limit = int(request.form.get("db_limit", 50)) if request.method == "POST" else 50
        source_csv = DEFAULT_CSV_PATH

        if request.method == "POST":
                action = request.form.get("action", "").strip().lower()

                upload = request.files.get("csv_file")
                if upload and upload.filename:
                        Path("data").mkdir(parents=True, exist_ok=True)
                        upload.save(UPLOADED_CSV_PATH)
                        source_csv = UPLOADED_CSV_PATH

                if action == "init_db":
                        try:
                                cfg = Config()
                                cfg.validate()
                                ensure_schema(cfg)
                                status = "ok"
                                message = "Schema initialization completed. sales_clean is ready."
                        except Exception as e:
                                status = "err"
                                message = f"Schema initialization failed: {e}"

                elif action == "run_pipeline":
                        try:
                                LAST_RESULTS = run_etl_flow(source_csv, load_mode)
                                status = "ok"
                                message = "Pipeline completed successfully and synced to CockroachDB."
                        except Exception as e:
                                LAST_RESULTS = None
                                status = "err"
                                message = f"Pipeline failed: {e}"

                elif action == "refresh_db":
                        status = "ok"
                        message = "Database view refreshed."

        source_df = pd.DataFrame()
        source_rows = 0
        try:
                source_df = pd.read_csv(source_csv)
                source_rows = len(source_df)
        except Exception:
                source_df = pd.DataFrame({"info": [f"Could not read {source_csv}"]})

        cfg = Config()
        db_status = "Unavailable"
        db_rows = 0
        db_df = pd.DataFrame({"info": ["Could not fetch DB table."]})

        try:
                cfg.validate()
                db_rows = fetch_total_count(cfg)
                db_df = fetch_table_data(cfg, limit=db_limit)
                db_status = "Connected"
        except Exception:
                db_status = "Unavailable"

        results = LAST_RESULTS
        cleaned_table = ""
        valid_table = ""
        transform_summary = {"raw_rows": 0, "valid_rows": 0, "removed_rows": 0}
        load_summary = {"mode": load_mode, "attempted": 0, "affected": 0, "skipped": 0, "total_rows": db_rows}

        if results:
                transform_summary = {
                        "raw_rows": len(results["raw"]),
                        "valid_rows": len(results["valid"]),
                        "removed_rows": len(results["raw"]) - len(results["valid"]),
                }
                load_summary = results["load_summary"]
                cleaned_table = df_to_html(results["cleaned"])
                valid_table = df_to_html(results["valid"])

        return render_template_string(
                TEMPLATE,
                status=status,
                message=message,
                load_mode=load_mode,
                db_limit=db_limit,
                db_status=db_status,
                db_rows=db_rows,
                source_rows=source_rows,
                source_csv=source_csv,
                source_table=df_to_html(source_df),
                results=results,
                transform_summary=transform_summary,
                load_summary=load_summary,
                cleaned_table=cleaned_table,
                valid_table=valid_table,
                db_table=df_to_html(db_df),
        )


if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000, debug=False)
