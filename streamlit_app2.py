import streamlit as st 
import pandas as pd

APP_TITLE = "title"
APP_SUB_TITLE = 'subtitle'

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    df = pd.read_csv('data/pivoted_data.csv')
    
    year = 2020
    state_name = 'Texas'
    disease_type = 0 
    field_name = 'Age_65+'
    metric_title = 'Mortality Rate'
        
    df = df[(df['Year'] == year) & (df['Disease_Type'] == disease_type)] 
    if state_name:
        df = df[df['LocationDesc'] == state_name]
    value = df[field_name].iloc[0]  # Extracting the first value from the Series
    st.metric(metric_title, value)
    
    st.write(df.shape)
    st.write(df.head())
    st.write(df.columns)
        

if __name__ == "__main__":
    main()
