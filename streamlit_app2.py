import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import uuid


APP_TITLE = "title"
APP_SUB_TITLE = "subtitle"


def display_time_filters(df):
    year_list = list(df["Year"].unique())
    year_list.sort()
    year = st.sidebar.selectbox("Year", year_list, len(year_list) - 1)
    st.header(f"{year}")
    return year


def display_state_filter(df, state_name):
    state_list = [""] + list(df["LocationDesc"].unique())
    state_list.sort()
    if not state_name:
        state_name = "Alabama"
    state_index = (
        state_list.index(state_name) if state_name and state_name in state_list else 0
    )
    return st.sidebar.selectbox("State", state_list, state_index)


def display_disease_type_filter():
    disease_type_dict = {
        0: "Major Cardiovascular Disease",
        1: "Heart Disease",
        2: "Acute Myocardial Infarction",
        3: "Coronary Heart Disease",
        4: "Heart Failure",
        5: "Cerebrovascular Disease",
        6: "Ischemic Stroke",
        7: "Hemorrhagic Stroke",
    }
    disease_type_options = list(disease_type_dict.values())
    disease_type_index = st.sidebar.selectbox(
        "Disease Type",
        range(len(disease_type_options)),
        format_func=lambda x: disease_type_dict[x],
    )
    return disease_type_index


def display_map(df, year):
    df = df[df["Year"] == year]

    map = folium.Map(
        location=[38, -96.5],
        zoom_start=4,
        scrollWheelZoom=False,
        tiles="CartoDB positron",
    )

    choropleth = folium.Choropleth(
        geo_data="data/us-state-boundaries.geojson",
        data=df,
        columns=("LocationDesc", "Overall_Overall", "Life_Expectancy"),
        key_on="feature.properties.name",
        line_opacity=0.8,
        highlight=True,
    )
    choropleth.geojson.add_to(map)

    df_indexed = df.set_index("LocationDesc")
    for feature in choropleth.geojson.data["features"]:
        state_name = feature["properties"]["name"]
        if state_name in list(df_indexed.index):
            feature["properties"][
                "mortality_rate"
            ] = "Mortality/100K Population: " + "{:,}".format(
                df_indexed.loc[state_name, "Overall_Overall"].iloc[0]
            )
            feature["properties"]["life_expectancy"] = "Life Expectancy: " + str(
                round(df_indexed.loc[state_name, "Life_Expectancy"].iloc[0])
            )
        else:
            feature["properties"]["mortality_rate"] = ""
            feature["properties"]["life_expectancy"] = ""

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            ["name", "mortality_rate", "life_expectancy"], labels=False
        )
    )

    unique_key = uuid.uuid4()

    st_map = st_folium(map, width=700, height=450, key=f"map_{year}_{unique_key}")

    state_name = ""
    if st_map["last_active_drawing"]:
        state_name = st_map["last_active_drawing"]["properties"]["name"]
    return state_name


def display_mortality_fact(
    df, year, state_name, disease_type, field_name, metric_title
):
    filtered_df = df[(df["Year"] == year) & (df["Disease_Type"] == disease_type)]
    if state_name:
        filtered_df = filtered_df[filtered_df["LocationDesc"] == state_name]

    value = (
        filtered_df[field_name].iloc[0] if not filtered_df[field_name].empty else "N/A"
    )
    st.metric(metric_title, value)


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    df_mortality = pd.read_csv("data/pivoted_data.csv")

    # Display Filters and Map
    year = display_time_filters(df_mortality)
    if year:
        state_name = display_map(df_mortality, year)
        state_name = display_state_filter(df_mortality, state_name)
        if state_name:
            disease_type = display_disease_type_filter()
            if disease_type is not None:
                st.subheader(f"{state_name} Mortality Facts" if state_name else "Mortality Facts")

    cols = st.columns(7)
    metrics_info = [
        ("Age_18-24", "Age 18-24 Mortality Rate"),
        ("Age_25-44", "Age 25-44 Mortality Rate"),
        ("Age_45-64", "Age 45-64 Mortality Rate"),
        ("Age_65+", "Age 65+ Mortality Rate"),
        ("Gender_Female", "Female Mortality Rate"),
        ("Gender_Male", "Male Mortality Rate"),
        ("Overall_Overall", "Overall Mortality Rate"),
    ]

    num_cols_per_row = 4
    num_metrics = len(metrics_info)
    num_rows = (num_metrics + num_cols_per_row - 1) // num_cols_per_row

    for i in range(num_rows):
        cols = st.columns(num_cols_per_row)
        for j in range(num_cols_per_row):
            idx = i * num_cols_per_row + j
            if idx < num_metrics:
                with cols[j]:
                    field_name, metric_title = metrics_info[idx]
                    display_mortality_fact(
                        df_mortality,
                        year,
                        state_name,
                        disease_type,
                        field_name,
                        metric_title,
                    )


if __name__ == "__main__":
    main()