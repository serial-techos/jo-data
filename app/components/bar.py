"""
Module for the bar component to use in streamlit app
"""

import plotly.express as px


class BarComponent:
    """
    Class for the bar component
    """

    def __init__(self, data, x, y):
        self.data = data
        self.x = x
        self.y = y

    def render(self, title: str, color: str, labels: dict):
        """
        Method to render the bar component

        """

        fig = px.bar(
            data_frame=self.data,
            x=self.x,
            y=self.y,
            color=color,
            log_y=True,
            title=title,
            labels=labels,
        )

        return fig
