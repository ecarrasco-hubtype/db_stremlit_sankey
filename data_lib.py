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
        node = diccionario["node"]
        if bot_id not in dict_group.keys():
            dict_group[bot_id] = []
        else:
            dict_group[bot_id].append(node)

    return dict_group


def get_sankey_fig(bot_id, start_date, end_date, node_source, min_width, max_steps):

    params = dict(
        node_source=node_source,
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
        max_steps=max_steps,
        min_width=min_width,
    )
    print(params)
    response = get_api('sankey', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])

    return response['data']


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


def get_handoff_top(bot_id, start_date, end_date, k=3):
    params = dict(
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
        k=k,
    )
    response = get_api('hand_over_nodes', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])
    else:
        return response['data']


def get_path_list(bot_id, start_date, end_date, k=5):
    params = dict(
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
        k=k,
    )
    response = get_api(
        'pipe_most_common_path_from_bot_with_hand_off', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])
    else:
        return response['data']


def get_loop_nodes(bot_id, start_date, end_date, k=5):
    params = dict(
        bot_id=bot_id,
        start_date=start_date,
        end_date=end_date,
        k=k,
    )
    response = get_api(
        'node_loops', params=params)
    if 'error' in response.keys():
        raise Exception(response['error'])
    else:
        return response['data']
