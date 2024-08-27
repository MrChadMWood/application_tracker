import logging
import os
import streamlit as st

# Expected use: st.set_page_config(layout=...)
layout_mode = 'wide'

# Hot reloading is set up via the `.streamlit/config.toml` file

# Environment Variables
logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
api_url = os.getenv('API_URL', 'http://api:8000')

# Configure logging
logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

