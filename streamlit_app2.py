import streamlit as st 
import pandas as pd

APP_TITLE = "title"
APP_SUB_TITLE = 'subtitle'

def display_mortality_facts(df, year, state_name, disease_type):
    filtered_df = df[(df['Year'] == year) & (df['Disease_Type'] == disease_type)]
    if state_name:
        filtered_df = filtered_df[filtered_df['LocationDesc'] == state_name]
    
    metrics = ['Age_18-24', 'Age_25-44', 'Age_45-64', 'Age_65+', 'Gender_Female', 'Gender_Male', 'Overall_Overall']
    metric_titles = ['Age 18-24 Mortality Rate', 'Age 25-44 Mortality Rate', 'Age 45-64 Mortality Rate',
                     'Age 65+ Mortality Rate', 'Female Mortality Rate', 'Male Mortality Rate', 'Overall Mortality Rate']

    for field_name, metric_title in zip(metrics, metric_titles):
        value = filtered_df[field_name].iloc[0] if not filtered_df[field_name].empty else "N/A"
        st.metric(metric_title, value)

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    df_mortality = pd.read_csv('data/pivoted_data.csv')
    
    year = 2020
    state_name = ''  # Adjust as needed
    disease_type = 0  # Adjust as needed
    
    display_mortality_facts(df_mortality, year, state_name, disease_type)

if __name__ == "__main__":
    main()
