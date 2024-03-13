import streamlit as st 
import pandas as pd

APP_TITLE = "title"
APP_SUB_TITLE = 'subtitle'


# def display_mortality_facts(year, state_name, disease_type, field_name, metric_title):
#     df = df[(df['Year'] == year) & (df['Disease_Type'] == disease_type)] 
#     if state_name:
#         df = df[df['LocationDesc'] == state_name]
#     value = df[field_name].iloc[0]  # Extracting the first value from the Series
#     st.metric(metric_title, value)

def display_mortality_facts(df, year, state_name, disease_type):
    df = df[(df['Year'] == year) & (df['Disease_Type'] == disease_type)]
    if state_name:
        df = df[df['LocationDesc'] == state_name]
    
    metrics = ['Age_18_24', 'Age_25_44', 'Age_45_64', 'Age_65+', 'Female', 'Male', 'Overall']
    metric_titles = ['Age 18-24 Mortality Rate', 'Age 25-44 Mortality Rate', 'Age 45-64 Mortality Rate',
                     'Age 65+ Mortality Rate', 'Female Mortality Rate', 'Male Mortality Rate', 'Overall Mortality Rate']

    for field_name, metric_title in zip(metrics, metric_titles):
        value = df[field_name].iloc[0] if not df[field_name].empty else "N/A"
        st.metric(metric_title, value)


def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    df_mortality = pd.read_csv('data/pivoted_data.csv')
    
    year = 2020
    state_name = ''
    disease_type = 0 
       
    display_mortality_facts(df_mortality, year, state_name, disease_type)
       

if __name__ == "__main__":
    main()
