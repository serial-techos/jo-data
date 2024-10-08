"""
Module for the map component to use in streamlit app
"""

from settings import settings
import plotly.express as px


class MapComponent:
    """
    Class for the map component
    """

    def __init__(self, data, lat_col, lon_col):
        self.data = data
        self.lat = lat_col
        self.lon = lon_col

    def render(self, title: str, hover_name: str, color: str, labels: dict, hover_data: list = None, center: dict = None, zoom: int = 4):
        """
        Method to render the map component

        """
        px.set_mapbox_access_token(
            settings.MAPBOX_TOKEN
        )
        fig = px.scatter_mapbox(
            self.data,
            lat=self.lat,
            lon=self.lon,
            hover_name=hover_name,
            height=700,
            color=color,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels=labels,
            title=title,
            center=center,
            custom_data=hover_data,
            zoom=zoom
        )
        fig.update_traces(cluster=dict(enabled=True), marker={"size": 20})

        return fig
