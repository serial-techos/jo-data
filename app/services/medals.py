"""Module to handle datasets data."""

import pandas as pd
from services.base import BaseService
from utils import create_color_from_str

class MedalsService(BaseService):
    """
    Service class to handle datasets data.
    """

    TABLE_NAME = "athletes_medals"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        data["is_france"] = data["code"] == "FRA"
        data["color"] = data["is_france"].apply(create_color_from_str)
        print(data)
        return data
