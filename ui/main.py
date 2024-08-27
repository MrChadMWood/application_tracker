import streamlit as st
import logging
from src.settings import api_url, layout_mode
from src.api import APIClient
from src.app import CRUDApp
from forms import endpoints, all_forms

logger = logging.getLogger(__name__)
st.set_page_config(layout=layout_mode)


if __name__ == "__main__":
    api_client = APIClient(base_url=api_url)
    app = CRUDApp(api_client, endpoints, all_forms)
    app.run()
