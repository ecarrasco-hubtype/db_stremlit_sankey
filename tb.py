import streamlit as st
import requests
import os
from dotenv import load_dotenv

try:
    load_dotenv()
    st.secrets['sankey'] = os.getenv('sankey')
    st.secrets['bot_id_nodes_from_org_id'] = os.getenv(
        'bot_id_nodes_from_org_id')

except FileNotFoundError as e:
    pass


def get_api(end_point, params=None):
    url = f'https://api.tinybird.co/v0/pipes/{end_point}.json'
    headers = {'Authorization': f'Bearer {st.secrets[end_point]}'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()
