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

    def render(self, title: str, labels: dict, color: str | None  = None, log_y: bool = True, orientation: str = 'h'):
        """
        Method to render the bar component

        """
        import plotly.graph_objects as go
        if color:
            marker = dict(
                color=self.data[color]
            )
        else :
            marker = None
        if orientation == 'h':
            x_data = self.data[self.y]
            y_data = self.data[self.x]
        else:
            x_data = self.data[self.x]
            y_data = self.data[self.y]
        fig = go.Figure(go.Bar(
                    x=x_data,
                    y=y_data,
                    orientation=orientation,
                    marker=marker,
                    text=self.data[self.y]
))

        fig.update_xaxes(categoryorder='total descending')
        fig.update_layout(
            title=title,
            xaxis_title=labels.get(self.x, self.x),
            yaxis_title=labels.get(self.y, self.y),
            yaxis_type='log' if log_y else None,
            margin=dict(l=0, r=0, t=30, b=0),
        )

        return fig
