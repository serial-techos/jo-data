"""
Main streamlit app
"""

import streamlit as st
from components.map import MapComponent
from components.bar import BarComponent
from services.datasets import DatasetService
from services.sites import SitesService
from settings import settings
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(layout="wide", page_title="JO Paris 2024", page_icon="🏅")
CONN_URI = settings.CONN_STRING


# Data loading functions
# Using st.cache_data to cache the data and prevent reloading it on every rerun
@st.cache_data
def load_datasets_catalog():
    return DatasetService(conn_uri=CONN_URI).process_data()


@st.cache_data
def load_sites_data():
    return SitesService(conn_uri=CONN_URI).process_data()

# Component loading functions
# Using st.cache_resource to cache the component and prevent reloading it on every rerun
@st.cache_resource
def get_map_component(data):
    return MapComponent(data=data, lat_col="latitude", lon_col="longitude")

@st.cache_resource
def get_bar_component(data):
    return BarComponent(data=data, x="title", y="records_count")

# Initialize the streamlit app state to prevent crash on when the app is reloaded
def initialize_state():
    if "num_sports" not in st.session_state:
        st.session_state.num_sports = 0


def display_metrics(metrics_dict):
    cols = st.columns(len(metrics_dict))
    for col, (label, value) in zip(cols, metrics_dict.items()):
        col.metric(label, value)


def filter_by_multiselect(df, column, selected_values):
    if selected_values:
        return df[df[column].str.split(",").apply(lambda x: any(val in x for val in selected_values))]
    return df

def display_dataset_records(datasets):
    themes_available = datasets["theme"].str.split(",").explode().unique()

    col1, _ = st.columns([0.5, 0.5])
    with col1:
        theme_selected = st.multiselect(
            "Thèmes",
            themes_available,
            placeholder="Cherchez des données par thème",
            label_visibility="collapsed",
        )

    filtered_datasets = filter_by_multiselect(datasets, "theme", theme_selected)

    bar_component = get_bar_component(filtered_datasets)
    bar_chart = bar_component.render(
        title="Nombre d'enregistrements par jeu de données",
        color="theme",
        labels={
            "records_count": "Nombre d'enregistrements",
            "title": "Nom du jeu de données",
            "theme": "Thème",
        },
    )
    st.plotly_chart(bar_chart)


def display_sites_map(sites):
    type_map = {"Olympique": "venue-olympic", "Paralympique": "venue-paralympic"}
    toggle_label = (
        "Paralympique" if st.session_state.get("type", False) else "Olympique"
    )
    filtered_sites = sites[sites["category_id"] == type_map[toggle_label]]
    sports_available = filtered_sites["sports"].str.split(",").explode().unique()

    # Update the number of sports
    st.session_state.num_sports = len(sports_available)
    # Update toggle_display with the current number of sports
    toggle_display = f"Jeux {toggle_label} ({st.session_state.num_sports} disciplines)"
    # Place the toggle after updating the display
    st.toggle(toggle_display, value=st.session_state.get("type", False), key="type")

    col1, _ = st.columns([0.5, 0.5])
    with col1:
        sports_selected = st.multiselect(
            "Sports",
            sports_available,
            placeholder="Cherchez des sites par discipline sportive",
            label_visibility="collapsed",
        )

    filtered_sites = filter_by_multiselect(filtered_sites, "sports", sports_selected)

    map_component = get_map_component(filtered_sites)
    map_chart = map_component.render(
        title="Sites de compétition",
        hover_name="nom_site",
        color="sports",
        labels={"nom_site": "Site de compétition", "sports": "Sports"},
    )
    st.plotly_chart(map_chart)


def main():
    st.title("Insights Paris 2024 🏅")

    # Load data
    datasets = load_datasets_catalog()
    sites = load_sites_data()

    # Initialize the streamlit app state
    initialize_state()

    tab1, tab2 = st.tabs(["Jeux de données", "Sites de compétition"])

    with tab1:
        dataset_metrics = {
            "Nombre de jeux de données": datasets.shape[0],
            "Datasets Géographiques": len(datasets[datasets["theme"] == "Geodata"]),
            "Dernière mise à jour": datasets["modified"].max().split("T")[0]
        }
        display_metrics(dataset_metrics)
        display_dataset_records(datasets)

    with tab2:
        sites_metrics = {
            "Disciplines sportives": len(sites["sports"].str.split(",").explode().unique()),
            "Sites Olympiques": len(sites[sites["category_id"] == "venue-olympic"]),
            "Sites Paralympiques": len(sites[sites["category_id"] == "venue-paralympic"])
        }
        display_metrics(sites_metrics)
        display_sites_map(sites)


if __name__ == "__main__":
    main()