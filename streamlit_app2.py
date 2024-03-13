import streamlit as st 
import pandas as pd
import folium
from streamlit_folium import st_folium


APP_TITLE = "title"
APP_SUB_TITLE = 'subtitle'


def display_mortality_fact(df, year, state_name, disease_type, field_name, metric_title):
    filtered_df = df[(df['Year'] == year) & (df['Disease_Type'] == disease_type)]
    if state_name:
        filtered_df = filtered_df[filtered_df['LocationDesc'] == state_name]
    
    value = filtered_df[field_name].iloc[0] if not filtered_df[field_name].empty else "N/A"
    st.metric(metric_title, value)
    
    
def display_map(df, year):
    df = df[df['Year'] == year] 
    
    map = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False, tiles='CartoDB positron')
    st_map = st_folium(map, width=700, height=450) 
    
    st.write(df.shape)
    st.write(df.head())
    st.write(df.columns)
    
    # choropleth = folium.Choropleth(
    #     geo_data='data/us-state-boundaries.geojson',
    #     data=df,
    #     columns=('LocationDesc', 'Overall_Overall'),
    #     key_on='feature.properties.name',
    #     line_opacity=0.8,
    #     highlight=True
    # )
    # choropleth.geojson.add_to(map)
    
    # df_indexed = df.set_index('LocationDesc')
    # for feature in choropleth.geojson.data['features']:
    #     state_name = feature['properties']['name']
    #     feature['properties']['mortality_rate'] = 'Overall_Overall: ' + '{:,}'.format(df_indexed.loc[state_name, 'Overall_Overall'][0]) if state_name in list(df_indexed.index) else ''
    #     feature['properties']['life_expectancy'] = 'Life_Expectancy: ' + str(round(df_indexed.loc[state_name, 'Life_Expectancy'][0])) if state_name in list(df_indexed.index) else ''

    # choropleth.geojson.add_child(
    #     folium.features.GeoJsonTooltip(['name', 'mortality_rate', 'life_expectancy'], labels=False)
    # )
    # st_map = st_folium(map, width=700, height=450) 
    

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    df_mortality = pd.read_csv('data/pivoted_data.csv')

    year = 2020
    state_name = ''  # Adjust as needed
    disease_type = 0  # Adjust as needed

    # Display Metrics 
    st.subheader(f'{state_name} Mortality Facts' if state_name else 'Mortality Facts')
    cols = st.columns(7)
    metrics_info = [
        ('Age_18-24', 'Age 18-24 Mortality Rate'),
        ('Age_25-44', 'Age 25-44 Mortality Rate'),
        ('Age_45-64', 'Age 45-64 Mortality Rate'),
        ('Age_65+', 'Age 65+ Mortality Rate'),
        ('Gender_Female', 'Female Mortality Rate'),
        ('Gender_Male', 'Male Mortality Rate'),
        ('Overall_Overall', 'Overall Mortality Rate')
    ]

    for col, (field_name, metric_title) in zip(cols, metrics_info):
        with col:
            display_mortality_fact(df_mortality, year, state_name, disease_type, field_name, metric_title)
    
    display_map(df_mortality, year)

if __name__ == "__main__":
    main()
