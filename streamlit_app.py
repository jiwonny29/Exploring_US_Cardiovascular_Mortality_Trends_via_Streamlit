import streamlit as st 
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = 'Fraud and Identity Theft Report'
APP_SUB_TITLE = 'Source: Federal Trade Commission'

def display_time_filter(df):
    year_list = sorted(df['Year'].unique())
    year = st.sidebar.selectbox('Year', year_list, index=len(year_list) - 1)
    st.header(f'{year}')
    return year 

def display_state_filter(df, state_name):
    state_list = [''] + sorted(df['LocationDesc'].unique())
    state_list.sort()
    state_index = state_list.index(state_name) if state_name and state_name in state_list else 0 
    return st.sidebar.selectbox('State', state_list, state_index)

def display_report_type_filter():
    report_types = st.sidebar.multiselect('Report Types', ['Overall', 'Sex', 'Age'])
    selected_options = []

    if 'Sex' in report_types:
        selected_sex = st.sidebar.multiselect('Select Sex', ['Male', 'Female'], ['Male', 'Female'])
        selected_options.extend(selected_sex)

    if 'Age' in report_types:
        age_options = ['Age 18-24', 'Age 25-44', 'Age 45-64', 'Age 65+']
        selected_age = st.sidebar.multiselect('Select Age Group', age_options, age_options)
        selected_options.extend(selected_age)

    if 'Overall' in report_types:
        selected_options.append('Overall')

    return selected_options

def display_map(df, year):
    df = df[df['Year'] == year]
    
    map = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False, tiles='CartoDB positron')
    
    choropleth = folium.Choropleth(
        geo_data='data/us-state-boundaries.geojson',
        data=df,
        columns=('LocationDesc', 'Data_Value'),
        key_on='feature.properties.name',
        line_opacity=0.8,
        highlight=True
    )
    choropleth.geojson.add_to(map)

    df_indexed = df.set_index('State Name')
    for feature in choropleth.geojson.data['features']:
        state_name = feature['properties']['name']
        feature['properties']['population'] = 'Population: ' + '{:,}'.format(df_indexed.loc[state_name, 'State Pop'][0]) if state_name in list(df_indexed.index) else ''
        feature['properties']['per_100k'] = 'Reports/100K Population: ' + str(round(df_indexed.loc[state_name, 'Reports per 100K-F&O together'][0])) if state_name in list(df_indexed.index) else ''

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name', 'population', 'per_100k'], labels=False)
    )
    
    st_map = st_folium(map, width=700, height=450)

    state_name = ''
    if st_map['last_active_drawing']:
        state_name = st_map['last_active_drawing']['properties']['name']
    return state_name


def display_data(df, year, state, report_types):
    df = df[(df['Year'] == year) & (df['LocationDesc'] == state)]





def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    # Load Data
    df_mortality = pd.read_csv('data/final.csv')
    
    # Display Filters and Map
    year = display_time_filter(df_mortality)
    state_name = display_map(df_mortality, year, state)
    state_name = display_state_filter(df_mortality, state_name)
    report_type = display_report_type_filter()
    
    # Display Metrics
    st.subheader(f'{state_name} {report_type} Mortality Facts')
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'State Fraud/Other Count', 'Overall Mortality', string_format='{:,}')
    with col2:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'Overall Median Losses Qtr', 'Male Mortality', is_median=True)
    with col3:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'Total Losses', 'Female Mortality')
    with col4:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'Total Losses', 'Age 45-64 Group Mortality')
    with col5:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'Total Losses', 'Age 65+ Group Mortality') 
    with col6:
        display_fraud_facts(df_mortality, year, quarter, report_type, state_name, 'Total Losses', 'Life Expectancy')       
                

if __name__ == '__main__':
    main()
