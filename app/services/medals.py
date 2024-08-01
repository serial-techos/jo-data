"""Module to handle datasets data."""

import pandas as pd
from services.base import BaseService


class MedalsService(BaseService):
    """
    Service class to handle datasets data.
    """

    TABLE_NAME = "medals"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        data["total"] = data["gold"] + data["silver"] + data["bronze"]
        data["is_france"] = "France" if data["code"] == "FRA" else "Not France"
        return data
