from abc import ABC, abstractmethod
import pandas as pd

class BaseLoader(ABC):
    @abstractmethod
    def load(self, df: pd.DataFrame):
        """Load transformed data to destination"""
        pass