"""Module to handle sites de competition data."""

import pandas as pd
from services.base import BaseService


class SitesService(BaseService):
    """
    Service class to handle sites de competition data.
    """

    TABLE_NAME = "paris_2024_sites_de_competition"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        # Some latitude and longitude values have a comma instead of a dot
        # We replace the comma with a dot and convert the values to float
        data["latitude"] = data["latitude"].str.replace(",", ".").astype(float)
        data["longitude"] = data["longitude"].str.replace(",", ".").astype(float)
        return data
