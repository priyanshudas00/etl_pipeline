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

    def _build_write_sql(self) -> str:
        if self.config.load_mode == "upsert":
            return """
                INSERT INTO sales_clean
                (sale_id, sale_date, product_name, quantity, price_per_unit, customer_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (sale_id) DO UPDATE SET
                    sale_date = EXCLUDED.sale_date,
                    product_name = EXCLUDED.product_name,
                    quantity = EXCLUDED.quantity,
                    price_per_unit = EXCLUDED.price_per_unit,
                    customer_phone = EXCLUDED.customer_phone
            """

        return """
            INSERT INTO sales_clean
            (sale_id, sale_date, product_name, quantity, price_per_unit, customer_phone)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (sale_id) DO NOTHING
        """

    def _get_total_rows(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM sales_clean")
        return int(self.cursor.fetchone()[0])

    def _row_to_values(self, row) -> tuple:
        return (
            int(row['sale_id']),
            row['date'],
            row['product_name'],
            int(row['quantity']),
            float(row['price_per_unit']),
            row['customer_phone'],
        )

    def _execute_load(self, write_sql: str, df: pd.DataFrame) -> int:
        affected = 0
        for _, row in df.iterrows():
            self.cursor.execute(write_sql, self._row_to_values(row))
            affected += max(self.cursor.rowcount, 0)
        return affected

    def load(self, df: pd.DataFrame):
        """
        Load cleaned DataFrame into sales_clean table.
        Mode 'skip' ignores duplicate sale_id rows.
        Mode 'upsert' updates existing rows on sale_id conflict.
        """
        self.connect()

        try:
            write_sql = self._build_write_sql()
            attempted = len(df)
            affected = self._execute_load(write_sql, df)

            # Commit all changes
            self.conn.commit()

            total_rows = self._get_total_rows()
            if self.config.load_mode == "skip":
                skipped = attempted - affected
                print(f"[LOAD] Attempted: {attempted} | Inserted: {affected} | Skipped: {skipped}")
            else:
                skipped = 0
                print(f"[LOAD] Attempted: {attempted} | Affected (insert/update): {affected}")
            print(f"[LOAD] Total rows now in sales_clean: {total_rows}")

            return {
                "mode": self.config.load_mode,
                "attempted": attempted,
                "affected": affected,
                "skipped": skipped,
                "total_rows": total_rows,
            }

        except psycopg.Error as e:
            self.conn.rollback()
            raise Exception(f"Error loading data: {e}")

        finally:
            self.disconnect()