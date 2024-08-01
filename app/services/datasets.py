"""Module to handle datasets data."""

import pandas as pd
from services.base import BaseService
from utils import create_color_from_str

datasets_used = ["paris_2024_sites_de_competition"]

class DatasetService(BaseService):
    """
    Service class to handle datasets data.
    """

    TABLE_NAME = "datasets"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        # Some titles have a prefix like "GEODATA -", "IDFM -", etc.
        # We remove the prefix to keep only the title
        data["title"] = data["title"].apply(
            lambda x: x.split("-")[1] if "-" in x else x
        )
        data["used"] = data["tablename"].apply(lambda x: x in datasets_used)
        data["color"] = data["used"].apply(create_color_from_str)
        return data
