from tb import get_api
from figures_lib import plotly_sankey
from dotenv import load_dotenv
load_dotenv()


def get_bot_list_nodes(org_id='98bb4472-1fba-4a2e-8a92-9e2ca0ad4ffc'):

    params = dict(
        org_id=org_id,
    )
    response = get_api('bot_id_nodes_from_org_id', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])

    dict_group = {}
    for diccionario in response['data']:
        bot_id = diccionario["bot_id"]
        faq_name = diccionario["faq_name"]
        if bot_id not in dict_group.keys():
            dict_group[bot_id] = []
        else:
            dict_group[bot_id].append(faq_name)
    return dict_group


def get_sankey_fig(bot_id, start_date, end_date, node_name):

    params = dict(
        node_name=node_name,
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
    )
    response = get_api('sankey', params=params)

    if 'error' in response.keys():
        raise Exception(response['error'])

    # for d in response['data']:
    #     if d['source_action'] == '':
    #         d['source_action'] = 'start'
    #     if d['target_action'] == '':
    #         d['target_action'] = 'end'

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
    data_flow['labels'] = [l.capitalize() for l in data_flow['labels']]

    return plotly_sankey(**data_flow)


def get_funnel(bot_id, start_date, end_date, node_names):
    params = dict(
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
        steps=node_names,
    )
    response = get_api('funnel', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])
    else:
        return response['data']


def get_handoff_list(bot_id, start_date, end_date):
    params = dict(
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
    )
    response = get_api('hand_over_nodes', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])
    else:
        return response['data']
