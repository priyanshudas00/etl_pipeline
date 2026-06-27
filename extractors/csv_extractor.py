import pandas as pd
from extractors.base_extractor import BaseExtractor

class CSVExtractor(BaseExtractor):
    def __init__(self, file_path):
        self.file_path = file_path

    def extract(self):
        """
        Extract data from CSV file and return as pandas DataFrame.
        """
        try:
            print(f"[EXTRACT] Reading data from: {self.file_path}")
            df = pd.read_csv(self.file_path)
            print(f"[EXTRACT] Loaded {len(df)} rows successfully.")
            return df
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error reading CSV file: {e}")