import pandas as pd
import re

class DataCleaner:
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the entire DataFrame:
        - Strip whitespace from string columns
        - Clean phone numbers
        - Convert date format
        - Fill missing quantity with 1
        """
        print("[CLEAN] Cleaning data...")

        # Strip whitespace from all string columns
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].str.strip()

        # Clean phone numbers
        df['customer_phone'] = df['customer_phone'].apply(self.clean_phone)

        # Standardize date format to YYYY-MM-DD
        df['date'] = df['date'].apply(self.clean_date)

        # Fill missing quantity with 1
        df['quantity'] = df['quantity'].fillna(1)

        print(f"[CLEAN] Cleaning completed. {len(df)} rows remaining.")
        return df

    def clean_phone(self, phone) -> str:
        """
        Clean phone number: extract 10 digits only.
        Returns None if invalid.
        """
        if pd.isna(phone):
            return None

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))

        # Return only if exactly 10 digits
        if len(digits) == 10:
            return digits
        else:
            return None

    def clean_date(self, date_str) -> str:
        """
        Convert various date formats to YYYY-MM-DD
        """
        if pd.isna(date_str):
            return None

        date_str = str(date_str).strip()

        # Handle DD-MM-YYYY
        if re.match(r'\d{2}-\d{2}-\d{4}', date_str):
            return pd.to_datetime(date_str, format='%d-%m-%Y').strftime('%Y-%m-%d')

        # Handle DD/MM/YYYY
        if re.match(r'\d{2}/\d{2}/\d{4}', date_str):
            return pd.to_datetime(date_str, format='%d/%m/%Y').strftime('%Y-%m-%d')

        # Already YYYY-MM-DD
        if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
            return date_str

        return None