import requests
import os


class conect_tb():
    def __init__(self):
        pass

    def get_api(self, end_point, params=None):
        self.url = f'https://api.tinybird.co/v0/pipes/{end_point}.json'
        token = os.getenv(end_point)
        headers = {'Authorization': f'Bearer {token}'}

        response = requests.get(self.url, params=params, headers=headers)
        return response.json()
