import streamlit as st 
import pandas as pd

APP_TITLE = "title"
APP_SUB_TITLE = 'subtitle'

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)
    
    df = pd.read_csv('data/final.csv')
    
    st.write(df.shape)
    st.write(df.head())
    st.write(df.columns)
    


if __name__ == "__main__":
    main()