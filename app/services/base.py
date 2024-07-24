"""
Base service class to handle data operations
"""

from abc import ABC, abstractmethod
from sqlalchemy import create_engine
import pandas as pd


class BaseService(ABC):
    """
    Base class for services
    """

    TABLE_NAME = None

    def __init__(self, conn_uri: str):
        self.engine = create_engine(url=conn_uri)

    @abstractmethod
    def get_data(self, include: list = []) -> pd.DataFrame:
        """
        Get data from the PostgreSQL database given the include columns and the table name.

        Returns:
            pd.DataFrame: data retrieved from the database
        """
        # handle include
        if include:
            columns = ", ".join(include)
        else:
            columns = "*"
        query = f"SELECT DISTINCT {columns} FROM {self.TABLE_NAME}"
        data = pd.read_sql(query, self.engine)
        return data

    @abstractmethod
    def process_data(self, **kwargs) -> pd.DataFrame:
        pass
