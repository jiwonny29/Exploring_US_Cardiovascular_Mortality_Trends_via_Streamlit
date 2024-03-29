import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import json
import plotly.express as px
import plotly.graph_objects as go


APP_TITLE = "US Cardiovascular Mortality Rates Analysis"
APP_SUB_TITLE = "Data Source: National Vital Statistics System"


@st.cache_data()
def load_geojson():
    with open("data/us-state-boundaries.geojson", "r") as f:
        return json.load(f)


def display_time_filters(df):
    year_list = list(df["Year"].unique())
    year_list.sort()
    year = st.sidebar.selectbox("Year", year_list, len(year_list) - 1)
    st.header(f"{year}")
    return year


def display_state_filter(df):
    state_list = list(df["LocationDesc"].unique())
    state_list.sort()
    state_name = st.sidebar.selectbox(
        "State", state_list, 0
    )  # Changed default index to 0
    return state_name


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


def display_map(df, year, geojson):
    # map_key = f"map_{year}"
    # if st.session_state.get(map_key) is None:
    #     st.session_state[map_key] = True  # Mark map as created for this year

    df = df[df["Year"] == year]

    map = folium.Map(
        location=[38, -96.5],
        zoom_start=4,
        scrollWheelZoom=False,
        tiles="CartoDB positron",
    )

    choropleth = folium.Choropleth(
        geo_data=geojson,
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
        feature["properties"]["mortality_rate"] = (
            "Mortality/100K Population: "
            + "{:,.0f}".format(
                round(df_indexed.loc[state_name, "Overall_Overall"].iloc[0])
            )
            if state_name in list(df_indexed.index)
            else ""
        )
        feature["properties"]["life_expectancy"] = (
            "Life Expectancy: "
            + str(round(df_indexed.loc[state_name, "Life_Expectancy"].iloc[0]))
            if state_name in list(df_indexed.index)
            else ""
        )
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(
            ["name", "mortality_rate", "life_expectancy"], labels=False
        )
    )
    st_map = st_folium(map, width=700, height=450)

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

    if isinstance(value, (int, float)):
        value = "{:,.0f}".format(value)

    st.metric(metric_title, value)


def plot_state_mortality_trend(df, state_name, disease_type):
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
    disease_name = disease_type_dict[disease_type]

    # Filter the data for the selected state and disease type
    state_data = df[
        (df["LocationDesc"] == state_name) & (df["Disease_Type"] == disease_type)
    ]
    state_data = state_data.groupby("Year")["Overall_Overall"].mean().reset_index()
    state_data["Year"] = state_data["Year"].astype(int)  # Convert years to int

    # Create an interactive line plot with Plotly
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=state_data["Year"],
            y=state_data["Overall_Overall"],
            mode="lines+markers",
            name="",
        )
    )

    # Update layout
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Mortality Rate (per 100K population)",
        hovermode="x",  # Show hover information for nearest data point
        showlegend=False,  # Hide legend
        width=700,  # Adjust width of the plot
        height=450,  # Adjust height of the plot
        margin=dict(l=20, r=20, t=20, b=20),  # Adjust margin
    )
    st.plotly_chart(fig)


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    df_mortality = pd.read_csv("data/data.csv")
    geojson = load_geojson()

    # Display Filters and Map
    year = display_time_filters(df_mortality)
    state_name = display_state_filter(df_mortality)  # Removed state_name argument
    disease_type = display_disease_type_filter()

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
    disease_name = disease_type_dict[disease_type]

    st.subheader(f"{state_name} {disease_name} Mortality Rates")

    # Comment below main header
    st.write(
        "Below are the mortality rates per 100K population for different age groups and genders."
    )

    cols = st.columns(7)
    metrics_info = [
        ("Age_18-24", "Death Rate for Ages 18-24"),
        ("Age_25-44", "Death Rate for Ages 25-44"),
        ("Age_45-64", "Death Rate for Ages 45-64"),
        ("Age_65+", "Death Rate for Ages 65+"),
        ("Gender_Female", "Female Fatality Rate"),
        ("Gender_Male", "Male Fatality Rate"),
        ("Overall_Overall", "Overall Fatality Rate"),
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

    # Plot overall mortality trend
    st.markdown(f"### Trend of Overall Mortality Rate for {state_name} ({disease_type_dict[disease_type]})")
    plot_state_mortality_trend(df_mortality, state_name, disease_type)

    # Assuming state_name and year are already defined
    st.subheader(f"{state_name} Population")
    filtered_df = df_mortality[
        (df_mortality["LocationDesc"] == state_name) & (df_mortality["Year"] == year)
    ]
    population = filtered_df.iloc[0]["population"]

    # Using st.metric with a label
    st.metric(label=f"Population in {year}", value=population)

    # Assuming state_name and year are already defined
    st.subheader(f"{state_name} Life Expectancy at Birth")
    life_expectancy = filtered_df.iloc[0]["Life_Expectancy"]

    # Using st.metric with a label
    life_expectancy_rounded = round(life_expectancy, 1)
    st.metric(label=f"Life Expectancy in {year}", value=life_expectancy_rounded)

    # Display map
    st.subheader(f"Comparison of Major CVD Mortality Rate Across States")
    display_map(df_mortality, year, geojson)


if __name__ == "__main__":
    main()
