"""
Main streamlit app
"""

import streamlit as st
from components.map import MapComponent
from components.bar import BarComponent
from services import DatasetService, SitesService, MedalsService, CountriesMedalsService, EventsService

from settings import settings
from dotenv import load_dotenv

load_dotenv()
from streamlit_geolocation import streamlit_geolocation
def search_string(s, search):
    return search in str(s).lower()

st.set_page_config(layout="wide", page_title="JO Paris 2024", page_icon="🏅")
CONN_URI = settings.CONN_STRING

print(f"Connection URI: {CONN_URI}")

# Data loading functions
# Using st.cache_data to cache the data and prevent reloading it on every rerun
@st.cache_data(ttl=180, show_spinner=False)
def load_datasets_catalog():
    return DatasetService(conn_uri=CONN_URI).process_data()


@st.cache_data(ttl=180, show_spinner=False)
def load_sites_data():
    return SitesService(conn_uri=CONN_URI).process_data()

@st.cache_data(ttl=180, show_spinner=False)
def load_medals_data():
    return MedalsService(conn_uri=CONN_URI).process_data(include=["athlete", "code", "gold", "silver", "bronze", "total"])

@st.cache_data(ttl=180, show_spinner=False)
def load_countries_medals_data():
    return CountriesMedalsService(conn_uri=CONN_URI).process_data()

@st.cache_data(ttl=180, show_spinner=False)
def load_events_data():
    return EventsService(conn_uri=CONN_URI).process_data()

@st.cache_resource(ttl=300, show_spinner=False)
def get_map_component(data):
    return MapComponent(data=data, lat_col="latitude", lon_col="longitude")

# @st.cache_resource
def get_bar_component(data, x="title", y="records_count"):
    return BarComponent(data=data, x=x, y=y)



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
        # color="theme",
        labels={
            "records_count": "Nombre d'enregistrements",
            "title": "Nom du jeu de données",
            "theme": "Thème",
        },
        orientation="v",
        color="color"
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

def display_medals_data(medals, athletes_medals):
    import plotly.graph_objects as go
    #join the two datasets on the country code to get the country name
    athletes_medals = athletes_medals.merge(medals[["code", "country"]], on="code", how="left")
    countries = medals.sort_values("gold", ascending=False)["country"].unique()
    
    # add selected countries to the session state
    if "selected_countries" not in st.session_state:
        st.session_state.selected_countries = countries[:5]
    
    # display multiselect to select countries
    selected_countries_command = st.multiselect(
        "Pays",
        countries,
        default=st.session_state.selected_countries,
        label_visibility="collapsed"
    )
    tab1, tab2 = st.tabs(["Médailles par pays", "Médailles par athlète"])
    with tab1:
        
        selected_countries = medals[medals["country"].isin(selected_countries_command)].copy()
        if selected_countries.shape[0] == 0:
            st.warning("Aucun pays sélectionné")
            return
        slider = st.slider(f"Pays affichés", value=[0, selected_countries.shape[0]], min_value=0, max_value=selected_countries.shape[0], step=1)
        medals_sorted = selected_countries.sort_values("gold", ascending=False).copy()
        df = medals_sorted.iloc[slider[0]:slider[1]].copy()
        # TODO: refactor this as a component(segmented bar)
        fig = go.Figure(data=[
            go.Bar(name='Or', y=df['flag'], x=df['gold'], marker_color='rgba(255, 215, 0, 0.7)', orientation='h',text=df['gold']),
            go.Bar(name='Argent', y=df['flag'], x=df['silver'], marker_color='rgba(192, 192, 192, 0.7)', orientation='h', text=df['silver']),
            go.Bar(name='Bronze', y=df['flag'], x=df['bronze'], marker_color='rgba(205, 127, 50, 0.7)', orientation='h', text=df['bronze']),
        ])
        fig.add_trace(go.Scatter(
            x=df['total'], 
            y=df['flag'],
            text=df['total'],
            mode='text',
            texttemplate='  %{text}',
            textposition='middle right',
            textfont=dict(
                size=18,
                color='black'
            ),
            showlegend=False
        ))

        fig.update_layout(
            title='Médailles par pays',
            xaxis_title='Nombre de médailles',
            barmode='stack',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            legend_title_text='Type de médaille',
            xaxis={'categoryorder':'total descending'},
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=0, r=0, t=30, b=0),
        )
        st.plotly_chart(fig)
    with tab2:
        selected_countries_athletes = athletes_medals[athletes_medals["country"].isin(selected_countries_command)].copy()
        selected_countries_athletes.sort_values("total", ascending=False, inplace=True)
        # capitalize the column names
        selected_countries_athletes.columns = selected_countries_athletes.columns.str.capitalize()
        st.dataframe(selected_countries_athletes[["Country", "Athlete", "Gold", "Silver", "Bronze", "Total",]], hide_index=True, )

def main():
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
    st.title("Insights Paris 2024 🏅")

    # Load data
    datasets = load_datasets_catalog()
    sites = load_sites_data()
    medals = load_countries_medals_data()
    athletes_medals = load_medals_data()

    
    # Initialize the streamlit app state
    initialize_state()

    medals_tab, celebration_sites, sites_tab, datasets_tab = st.tabs(["Médailles", "Lieux de célébration","Sites de compétition", "Jeux de données"])

    with datasets_tab:
        dataset_metrics = {
            "Nombre de jeux de données": datasets.shape[0],
            "Datasets Géographiques": len(datasets[datasets["theme"] == "Geodata"]),
            "Dernière mise à jour": datasets["modified"].max().split("T")[0]
        }
        display_metrics(dataset_metrics)
        display_dataset_records(datasets)

    with celebration_sites:
        st.markdown("**Découvrez les lieux de célébration/fan zones des JO Paris 2024!**")
        events = load_events_data()
        events_selected = events.copy()

        events_metrics = {
            "Lieux de célébrations": events.shape[0],
            "Lieux de diffusions d'épreuves": len(events[events["subcategory_code"] == "games-broadcasting"]),
            "Lieux de festivité/fan zones": len(events[events["subcategory_code"] == "around-the-games"])
        }
        display_metrics(events_metrics)
        
        st.markdown("**Recherche par mot-clé**")
        search_query = st.text_input("Recherche", "", placeholder="Montparnasse, Mairie, Concert, etc..", label_visibility="collapsed")
        st.markdown("**Près de moi**")
        my_geolocation = streamlit_geolocation()
        if search_query:
            if "," in search_query:
                search_queries = search_query.split(",")
                mask = events_selected.apply(lambda x: x.map(lambda s: any(search_string(s, search_query) for search_query in search_queries)))
            else:
                mask = events_selected.apply(lambda x: x.map(lambda s: search_string(s, search_query)))
            events_selected = events_selected.loc[mask.any(axis=1)]

        # st.dataframe(events_selected, hide_index=True)
        center = {"lat": my_geolocation["latitude"], "lon": my_geolocation["longitude"]}
        
        map_component = get_map_component(events_selected)
        #if lat and lon are not None, render the map with the center as the geolocation
        map_chart = map_component.render(
            title=f"Lieux de célébration({events_selected.shape[0]})",
            hover_name="title",
            hover_data=["title","category_id", "subcategory_code", "address"],
            color="subcategory_code_gold",
            labels={"title": "Lieu de célébration", "category_id": "Catégorie"},
        )
        if my_geolocation["latitude"] and my_geolocation["longitude"]:
            map_chart = map_component.render(
                title=f"Lieux de célébration({events_selected.shape[0]})",
                hover_name="title",
                hover_data=["title","category_id", "subcategory_code", "address"],
                color="subcategory_code_gold",
                labels={"title": "Lieu de célébration", "category_id": "Catégorie", "subcategory_code_gold": "Type de célébration"},
                center=center,
                zoom=13
            )
        map_chart.update_traces(hovertemplate="<b>%{customdata[0]}</b> <br><br> Address: %{customdata[3]}")
        map_chart.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        legend_title_text="Type de célébration")
 
        st.plotly_chart(map_chart)

    with sites_tab:
        sites_metrics = {
            "Disciplines sportives": len(sites["sports"].str.split(",").explode().unique()),
            "Sites Olympiques": len(sites[sites["category_id"] == "venue-olympic"]),
            "Sites Paralympiques": len(sites[sites["category_id"] == "venue-paralympic"])
        }
        display_metrics(sites_metrics)
        display_sites_map(sites)
    
    with medals_tab:
        display_medals_data(medals, athletes_medals) 

if __name__ == "__main__":
    main()
