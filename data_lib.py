from tb import conect_tb
from figures_lib import plotly_sankey
import os
from dotenv import load_dotenv
load_dotenv()


class data_getter():
    def __init__(self):
        self.tb = conect_tb()

    def set_tolken(self, token):
        self.token = token
        self.tb = conect_tb(self.token)

    def get_bot_list(self, org_id='98bb4472-1fba-4a2e-8a92-9e2ca0ad4ffc'):
        token = os.getenv('token_list_bot_ids')
        headers = {'Authorization': f'Bearer {token}'}
        params = dict(
            org_id=org_id,
        )
        response = self.tb.get_api(
            'bot_list_from_org_id', params=params, headers=headers)
        if 'error' in response.keys():
            raise Exception(response['error'])
        else:
            return [d['bot_id'] for d in response['data']]

    def get_node_list(self, bot_id):
        params = dict(
            bot_id=bot_id,
            token=os.getenv('token_node_list')
        )
        response = self.tb.get_api('node_list_from_bot_id', params=params)
        if 'error' in response.keys():
            raise Exception(response['error'])
        else:
            return [d['faq_name'] for d in response['data']]

    def get_sankey_fig(self, bot_id, start_date, end_date, node_name, grouper=None):
        if node_name == '-':
            node_name = ''
        token = os.getenv('token_sank')
        headers = {'Authorization': f'Bearer {token}'}
        params = dict(
            node_name=node_name,
            grouper=grouper,
            bot_id=bot_id,
            start_date=start_date,
            end_date=end_date,
        )
        response = self.tb.get_api(
            'bot_sankey', params=params,  headers=headers)

        if 'error' in response.keys():
            raise Exception(response['error'])

        for d in response['data']:
            if d['source_action'] == '':
                d['source_action'] = 'start'
            if d['target_action'] == '':
                d['target_action'] = 'end'

        data_flow = {
            'title': "",
            'labels': list(set([d['source_action'] for d in response['data']] + [d['target_action'] for d in response['data']]))
        }

        data_flow['value'] = [d['transition_count']
                              for d in response['data']]
        data_flow['source'] = [data_flow['labels'].index(
            d['source_action']) for d in response['data']]
        data_flow['target'] = [data_flow['labels'].index(
            d['target_action']) for d in response['data']]

        if 'grouper' in response['data'][0].keys():
            data_flow['grouper'] = [d['grouper'] for d in response['data']]
        data_flow['labels'] = [str.replace(
            l, '_', ' ').upper() for l in data_flow['labels']]
        return plotly_sankey(**data_flow)

    def get_funnel(self, bot_id, start_date, end_date, node_names, grouper=None):
        token = os.getenv('token_funnel')
        headers = {'Authorization': f'Bearer {token}'}
        params = dict(
            bot_id=bot_id,
            start_date=start_date,
            end_date=end_date,
            steps=node_names,
        )
        response = self.tb.get_api('funnel', params=params,  headers=headers)

        if 'error' in response.keys():
            raise Exception(response['error'])
        else:
            return response['data']
