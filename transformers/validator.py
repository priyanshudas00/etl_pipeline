import pandas as pd

class DataValidator:
    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate cleaned DataFrame:
        - Remove rows with missing phone numbers
        - Remove rows with negative or zero quantity
        - Remove rows with invalid dates
        Returns clean validated DataFrame
        """
        print(f"[VALIDATE] Starting validation. Total rows: {len(df)}")

        # Keep only rows with valid phone number (not None/NaN)
        df = df.dropna(subset=['customer_phone'])

        # Remove negative or zero quantity
        df = df[df['quantity'] > 0]

        # Remove rows with invalid date
        df = df.dropna(subset=['date'])

        # Remove duplicate sale_ids
        df = df.drop_duplicates(subset=['sale_id'], keep='first')

        print(f"[VALIDATE] Validation completed. {len(df)} valid rows remaining.")
        return df