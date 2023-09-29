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

    def get_bot_list(self):
        params = dict(
                        org_id = '4003c2f4-5e8c-43cb-a70f-c4bc128b02fd',
                        token = os.getenv('token_list_bot_ids')
                    )
        response = self.tb.get_api('bot_list_from_org_id', params=params)
        if 'error' in response.keys():
            print('ERROR')
            return response['error']
        else:
            return [d['bot_id'] for d in response['data']]

    def get_sankey_fig(self, bot_id, start_date, end_date):
        params = dict(
                        bot_id = bot_id,
                        start_date = start_date,
                        end_date = end_date,
                        token = os.getenv('token_sanken')
                )
        response = self.tb.get_api('bot_sankey', params=params)
        if 'error' in response.keys():
            print('ERROR')
            return response['error']
        else:
            data_flow = {
                'title': "Multiasistencia",
                'labels': list(set([d['source_action'] for d in response['data']] + [d['target_action'] for d in response['data']]))
            }
            data_flow['source'] = [data_flow['labels'].index(d['source_action']) for d in response['data']]
            data_flow['target'] = [data_flow['labels'].index(d['target_action']) for d in response['data']]
            data_flow['value'] = [d['transition_count'] for d in response['data']]

        return plotly_sankey(**data_flow)
