from data_lib import get_bot_list_nodes, get_sankey_fig, get_funnel, get_handoff_top, get_path_list, get_loop_nodes
from figures_lib import plotly_sankey

import streamlit as st
# from streamlit_sortables import sort_items

import datetime as dt
from config import bot_id_name_dic

import importlib
import data_lib
importlib.reload(data_lib)

today = dt.datetime.today()


def clean_node_names(x):
    if x == '-':
        return 'START'
    return x.replace('_', ' ').capitalize().upper()


def init_st():
    if 'init' not in st.session_state:
        st.set_page_config(layout="wide")
        st.session_state['init'] = True
        st.session_state['bot_id'] = None
        st.session_state['node_source'] = None
        st.session_state['start_date'] = None
        st.session_state['end_date'] = None
        st.session_state['dict_bot_id_nodes'] = get_bot_list_nodes()
        st.session_state['min_date'] = dt.datetime.strptime(
            '2023-09-12', '%Y-%m-%d')

        st.session_state['sankey_data'] = None
        st.session_state['n_filter'] = None
        st.session_state['max_len_path'] = None


def main_selector():
    st_logo, st_org, _ = st.columns([2, 3, 10])
    st_logo.write('')
    st_logo.image('./img/ht_logo.png', width=150)
    st_org.header('MULTIASISTENCIA')
    st_1, st_2, st_3, st_4, _ = st.columns([2, 3, 1, 1, 8])

    st.session_state['list_bots'] = st.session_state['dict_bot_id_nodes'].keys()
    bot_id = st_1.selectbox(
        'BOT', st.session_state['list_bots'], index=None, format_func=lambda x: bot_id_name_dic.get(x, x))

    st.session_state['list_nodes'] = st.session_state['dict_bot_id_nodes'].get(
        bot_id, [])
    node_source = st_2.selectbox(
        'SOURCE NODE', st.session_state['list_nodes'], format_func=clean_node_names, index=None)

    start_date = st_3.date_input(
        'FROM', value=today - dt.timedelta(days=21), min_value=st.session_state['min_date'], max_value=today, key=None)

    end_date = st_4.date_input(
        'TO', value=today, min_value=st.session_state['min_date'], max_value=today, key=None)

    if bot_id != st.session_state['bot_id'] or \
            node_source != st.session_state['node_source'] or \
            start_date != st.session_state['start_date'] or \
            end_date != st.session_state['end_date']:
        st.session_state['bot_id'] = bot_id
        st.session_state['node_source'] = node_source
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date
        st.session_state['update_sankey'] = True
        st.session_state['start_date'] = st.session_state['start_date'].strftime(
            '%Y-%m-%d')
        st.session_state['end_date'] = st.session_state['end_date'].strftime(
            '%Y-%m-%d')


def sk_section():

    set_necessary_inputs = all(
        [st.session_state['bot_id'], st.session_state['start_date'], st.session_state['end_date']])

    if set_necessary_inputs and st.session_state['update_sankey']:
        st.session_state['update_sankey'] = False

        st.session_state['sankey_data'] = get_sankey_fig(bot_id=st.session_state['bot_id'],
                                                         start_date=st.session_state['start_date'],
                                                         end_date=st.session_state['end_date'],
                                                         node_source=st.session_state['node_source'],
                                                         n_filter=st.session_state['n_filter']
                                                         )

    if st.session_state['sankey_data'] is not None:
        max_len_sanky = max([int(d['target_action'][-3:])
                             for d in st.session_state['sankey_data']])
        transitions_values = [d['transition_count']
                              for d in st.session_state['sankey_data']]
        max_transitions = max(transitions_values)

        st_1, _, st_2 = st.columns([2, 1, 20])

        st_1.header(' ')
        st_1.header(' ')
        st_1.header(' ')
        st_1.header(' ')
        st_1.header(' ')
        st.session_state['n_filter'] = st_1.slider(
            'MIN. BAND WIDTH', value=1, min_value=1, max_value=max_transitions, step=1)
        st_1.header(' ')
        st.session_state['max_len_path'] = st_1.slider(
            'MAX. PATH LENGTH', value=max_len_sanky//4, min_value=1, max_value=max_len_sanky, step=1)

        st_2.plotly_chart(plotly_sankey(st.session_state['sankey_data'],
                                        n_filter=st.session_state['n_filter'],
                                        max_path_len=st.session_state['max_len_path'],
                                        title='',
                                        ),
                          use_container_width=True,
                          config={
            'displaylogo': False}
        )
    else:
        for _ in range(5):
            st.header(' ')
        _, st_logo, _ = st.columns([10, 3, 10])
        st_logo.image('./img/ht_circle.png', width=150, use_column_width=True)
        st_logo.warning('Select a bot and date range')


# NOT USED:
# def funnel_section():
#     st.header('Choose your funnel steps')

#     funnel_nodes_not_ordered = st.multiselect(
#         'Funnel Nodes', st.session_state.get('list_nodes', []), format_func=clean_node_names, max_selections=10)

#     if funnel_nodes_not_ordered != st.session_state.get('funnel_nodes_not_ordered', []):
#         st.session_state['funnel_nodes_not_ordered'] = funnel_nodes_not_ordered

#     st.session_state['funnel_nodes'] = sort_items(
#         st.session_state.get('funnel_nodes_not_ordered', []))

#     more_than_one_node = len(st.session_state['funnel_nodes']) > 1
#     all_inputs_set = all([st.session_state['bot_id'], st.session_state['start_date'],
#                          st.session_state['end_date'], more_than_one_node])
#     if all_inputs_set and st.button('Update funnel'):
#         update_funnel()

#     if st.session_state['df'] is not None:
#         st.bar_chart(st.session_state['df'], x='stage', y='value')


# def update_funnel():
#     funnel = get_funnel(
#         bot_id=st.session_state['bot_id'],
#         start_date=st.session_state['start_date'],
#         end_date=st.session_state['end_date'],
#         node_names=','.join(st.session_state['funnel_nodes'])
#     )
#     df = pd.DataFrame(funnel)
#     try:
#         df['stage'] = df['funnel_stage'].astype(
#             str) + '-' + df['step_name']
#         st.session_state['df'] = df
#     except Exception as e:
#         print(e)
#         st.session_state['df'] = None
