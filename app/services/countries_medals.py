"""Module to handle datasets data."""

import pandas as pd
from services.base import BaseService
from utils import create_color_from_str


class CountriesMedalsService(BaseService):
    """
    Service class to handle datasets data.
    """

    TABLE_NAME = "countries_medals"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        # when country is France, we add a column is_france with value France
        # otherwise we add a column is_france with value Not France
        data["is_france"] = data["code"] == "FRA"
        data["color"] = data["is_france"].apply(create_color_from_str)
        return data
