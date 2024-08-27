import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TableDisplay:
    def __init__(self, api_client):
        self.api_client = api_client

    def show_table(self, endpoint):
        data = self.api_client.fetch_data(endpoint)
        if data:
            df = pd.DataFrame(data).set_index('id')
            st.dataframe(df)
        else:
            st.write("No data available.")
