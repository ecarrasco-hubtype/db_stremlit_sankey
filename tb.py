import streamlit as st
import requests


def get_api(end_point, params=None):
    url = f'https://api.tinybird.co/v0/pipes/{end_point}.json'
    headers = {'Authorization': f'Bearer {st.secrets[end_point]}'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()
