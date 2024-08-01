"""Module to get events data from pgsql db to pandas dataframe"""

import pandas as pd
from services.base import BaseService


class EventsService(BaseService):
    TABLE_NAME = "paris_2024_evenements_olympiade_culturelle"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        data["latitude_c"] = data["latitude_c"].replace("..", ".").astype(float)
        data["longitude_c"] = data["longitude_c"].str.replace("..", ".").astype(float)
        data = data[data["latitude_c"].notnull() & data["longitude_c"].notnull()]
        return data
