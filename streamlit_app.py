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

def display_state_filter(df):
    state_list = [''] + sorted(df['LocationDesc'].unique())
    state = st.sidebar.selectbox('State', state_list)
    return state

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

def display_map(df, year, state):
    map = folium.Map(location=[38, -96.5], zoom_start=4, scrollWheelZoom=False, tiles='CartoDB positron')
    
    filtered_df = df[(df['Year'] == year) & (df['LocationDesc'] == state)]
    
    choropleth = folium.Choropleth(
        geo_data='data/us-state-boundaries.geojson',
        data=filtered_df,
        columns=('State Name', 'State Total Reports Quarter'),
        key_on='feature.properties.name',
        line_opacity=0.8,
        highlight=True
    )
    choropleth.geojson.add_to(map)

    df_indexed = filtered_df.set_index('State Name')
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
    filtered_df = df[(df['Year'] == year) & (df['LocationDesc'] == state)]
    if not filtered_df.empty:
        st.subheader(f'Mortality Rates and Life Expectancy in {state}, {year}')
        for report_type in report_types:
            st.write(f'{report_type}:')
            if report_type == 'Life Expectancy':
                st.write(filtered_df['Life Expectancy'])
            elif report_type == 'Overall':
                st.write(filtered_df[['Overall']])
            else:
                selected_columns = [col for col in filtered_df.columns if any(option in col for option in report_type.split())]
                st.write(filtered_df[selected_columns])
    else:
        st.write('No data available for the selected filters.')

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    # Load Data
    df = pd.read_csv('data/final.csv')

    year = display_time_filter(df)
    state = display_state_filter(df)
    report_types = display_report_type_filter()

    display_data(df, year, state, report_types)  

if __name__ == '__main__':
    main()
