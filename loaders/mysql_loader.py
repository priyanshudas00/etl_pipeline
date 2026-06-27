import psycopg
import pandas as pd
from loaders.base_loader import BaseLoader
from models.config import Config

class MySQLLoader(BaseLoader):
    def __init__(self, config: Config):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection"""
        try:
            self.config.validate()
            self.conn = psycopg.connect(self.config.db_url, **self.config.connection_options())
            self.cursor = self.conn.cursor()
            print("[LOAD] Connected to CockroachDB.")
        except psycopg.Error as e:
            raise Exception(f"Database connection failed: {e}")

    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("[LOAD] Database connection closed.")

    def load(self, df: pd.DataFrame):
        """
        Load cleaned DataFrame into sales_clean table.
        Uses ON CONFLICT DO NOTHING to skip duplicate sale_id rows.
        """
        self.connect()

        try:
            insert_sql = """
                INSERT INTO sales_clean
                (sale_id, sale_date, product_name, quantity, price_per_unit, customer_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (sale_id) DO NOTHING
            """

            records_inserted = 0
            for _, row in df.iterrows():
                values = (
                    int(row['sale_id']),
                    row['date'],
                    row['product_name'],
                    int(row['quantity']),
                    float(row['price_per_unit']),
                    row['customer_phone']
                )
                self.cursor.execute(insert_sql, values)
                records_inserted += self.cursor.rowcount

            # Commit all changes
            self.conn.commit()
            print(f"[LOAD] Successfully inserted {records_inserted} records into sales_clean table.")

        except psycopg.Error as e:
            self.conn.rollback()
            raise Exception(f"Error loading data: {e}")

        finally:
            self.disconnect()