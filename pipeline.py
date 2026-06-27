"""
Main ETL Pipeline Runner.
Command: python pipeline.py
"""
import time
from engine.etl_engine import ETLEngine
from extractors.csv_extractor import CSVExtractor
from loaders.mysql_loader import MySQLLoader
from models.config import Config
from transformers.cleaner import DataCleaner
from transformers.validator import DataValidator

def run_pipeline():
    print("=" * 50)
    print("ETL PIPELINE STARTED")
    print("=" * 50)

    start_time = time.time()

    try:
        engine = ETLEngine(
            extractor=CSVExtractor("data/sales.csv"),
            cleaner=DataCleaner(),
            validator=DataValidator(),
            loader=MySQLLoader(Config()),
        )
        report = engine.run()

        print("\n" + "-" * 30)
        print("TRANSFORMATION SUMMARY:")
        print(f"  Raw rows:     {report.transformation.raw_rows}")
        print(f"  Valid rows:   {report.transformation.valid_rows}")
        print(f"  Removed rows: {report.transformation.removed_rows}")
        print("-" * 30 + "\n")

        print("\n" + "-" * 30)
        print("LOAD SUMMARY:")
        print(f"  Mode:        {report.load.mode}")
        print(f"  Attempted:   {report.load.attempted}")
        if report.load.mode == 'skip':
            print(f"  Inserted:    {report.load.affected}")
            print(f"  Skipped:     {report.load.skipped}")
        else:
            print(f"  Affected:    {report.load.affected}")
        print(f"  Table rows:  {report.load.total_rows}")
        print("-" * 30)

        print("\n✅ ETL Pipeline completed successfully!")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        exit(1)

    finally:
        elapsed = time.time() - start_time
        print(f"⏱️  Total time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    run_pipeline()