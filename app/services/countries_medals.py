"""Module to handle datasets data."""

import pandas as pd
from services.base import BaseService
from utils import create_color_from_str
from flag import flag

countries_flags_mapping = {
    "CHN": "CN",
    "KOR": "KR",
    "SWE": "SE",
    "KAZ": "KZ",
    "UKR": "UA",
    "CHI": "CL",
    "SUI": "CH",
    "POL": "PL",
    "TPE": "TW",
    "JAM": "JM",

}
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
        #turn the 3 chars codee into 2 chars code using the countries_flags_mapping or keep the first 2 chars
        data["processed_code"] = data["code"].apply(lambda x: countries_flags_mapping.get(x, x[:2]))
        data["flag"] = data["processed_code"].apply(flag)
        data["flag"] = data["code"] + "(" + data["flag"] + ")"
        return data
