"""Module to get events data from pgsql db to pandas dataframe"""

import pandas as pd
from services.base import BaseService


class EventsService(BaseService):
    TABLE_NAME = "games_map_events_fr"

    def get_data(self, include: list = []) -> pd.DataFrame:
        return super().get_data(include)

    def process_data(self, **kwargs):
        include = kwargs.get("include", [])
        data = self.get_data(include)
        data = data[data["category_id"] == "celebration_event"]
        data["subcategory_code_gold"] = data["subcategory_code"].str.replace("_", " ").str.replace("-", " ").str.title()

        data["latitude"] = data["latitude"].astype(float)
        data["longitude"] = data["longitude"].astype(float)
        data = data[data["latitude"].notnull() & data["longitude"].notnull()]
        return data
