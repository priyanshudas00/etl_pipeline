"""
Run this script to create the sales_clean table.
Command: python setup_db.py
"""
import psycopg
from models.config import Config

config = Config()
config.validate()

conn = psycopg.connect(config.db_url, **config.connection_options())

cursor = conn.cursor()

# Create table
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
cursor.execute(create_table_sql)
print("Table 'sales_clean' ready.")

conn.commit()

cursor.close()
conn.close()
print("Setup complete!")