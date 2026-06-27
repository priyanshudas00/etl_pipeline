"""
Main ETL Pipeline Runner.
Command: python pipeline.py
"""
import time
from extractors.csv_extractor import CSVExtractor
from transformers.cleaner import DataCleaner
from transformers.validator import DataValidator
from loaders.mysql_loader import MySQLLoader
from models.config import Config

def run_pipeline():
    print("=" * 50)
    print("ETL PIPELINE STARTED")
    print("=" * 50)

    start_time = time.time()

    try:
        # ========== EXTRACT ==========
        extractor = CSVExtractor("data/sales.csv")
        raw_data = extractor.extract()

        # ========== TRANSFORM ==========
        cleaner = DataCleaner()
        cleaned_data = cleaner.clean_dataframe(raw_data)

        validator = DataValidator()
        valid_data = validator.validate(cleaned_data)

        # Show summary
        print("\n" + "-" * 30)
        print("TRANSFORMATION SUMMARY:")
        print(f"  Raw rows:     {len(raw_data)}")
        print(f"  Valid rows:   {len(valid_data)}")
        print(f"  Removed rows: {len(raw_data) - len(valid_data)}")
        print("-" * 30 + "\n")

        # ========== LOAD ==========
        config = Config()
        loader = MySQLLoader(config)
        loader.load(valid_data)

        print("\n✅ ETL Pipeline completed successfully!")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        exit(1)

    finally:
        elapsed = time.time() - start_time
        print(f"⏱️  Total time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    run_pipeline()