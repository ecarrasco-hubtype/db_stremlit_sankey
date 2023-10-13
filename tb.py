import requests
import os


def get_api(end_point, params=None):
    url = f'https://api.tinybird.co/v0/pipes/{end_point}.json'
    headers = {'Authorization': f'Bearer {os.getenv(end_point)}'}
    response = requests.get(url, params=params, headers=headers)
    return response.json()
