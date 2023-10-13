from data_lib import get_bot_list_nodes, get_sankey_fig, get_funnel

import streamlit as st
from streamlit_sortables import sort_items

import pandas as pd
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
        st.session_state['init'] = True
        st.session_state['bot_id'] = None
        st.session_state['node_name'] = None
        st.session_state['start_date'] = None
        st.session_state['end_date'] = None
        st.session_state['dict_bot_id_nodes'] = get_bot_list_nodes()
        st.session_state['min_date'] = dt.datetime.strptime(
            '2023-09-12', '%Y-%m-%d')
        st.session_state['df'] = None

        st.session_state['fig_sankey'] = None
        st.session_state['fig_funnel'] = None


def main_selector():
    st.header('Multiasistencia')
    st_1, st_2, =  st.columns([3, 2])
    st_3, st_4, _, _ = st.columns([1, 1, 1, 2])

    st.session_state['list_bots'] = st.session_state['dict_bot_id_nodes'].keys()
    st.session_state['bot_id'] = st_1.selectbox(
        'Bot', st.session_state['list_bots'], index=None, format_func=lambda x: bot_id_name_dic.get(x, x))

    st.session_state['list_nodes'] = st.session_state['dict_bot_id_nodes'].get(
        st.session_state['bot_id'], [])

    st.session_state['node_name'] = st_2.selectbox(
        'Origin Node', st.session_state['list_nodes'], format_func=clean_node_names, index=None)

    st.session_state['start_date'] = st_3.date_input(
        'FROM', value=today - dt.timedelta(days=21), min_value=st.session_state['min_date'], max_value=today, key=None)
    st.session_state['end_date'] = st_4.date_input(
        'TO', value=today, min_value=st.session_state['min_date'], max_value=today, key=None)

    st.session_state['start_date'] = st.session_state['start_date'].strftime(
        '%Y-%m-%d')
    st.session_state['end_date'] = st.session_state['end_date'].strftime(
        '%Y-%m-%d')


def sk_section():
    st.header('SANKLEY')
    set_necessary_inputs = all(
        [st.session_state['bot_id'], st.session_state['start_date'], st.session_state['end_date']])
    if set_necessary_inputs and st.button('Update Sankey'):
        st.session_state['fig_sankey'] = get_sankey_fig(bot_id=st.session_state['bot_id'],
                                                        start_date=st.session_state['start_date'],
                                                        end_date=st.session_state['end_date'],
                                                        node_name=st.session_state['node_name'],
                                                        #    grouper=st.session_state['grouper']
                                                        )
    if st.session_state['fig_sankey']:
        st.plotly_chart(st.session_state['fig_sankey'], use_container_width=False,
                        config={'displaylogo': False})


def funnel_section():
    st.header('Choose your funnel steps')

    funnel_nodes_not_ordered = st.multiselect(
        'Funnel Nodes', st.session_state.get('list_nodes', []), format_func=clean_node_names, max_selections=10)

    if funnel_nodes_not_ordered != st.session_state.get('funnel_nodes_not_ordered', []):
        st.session_state['funnel_nodes_not_ordered'] = funnel_nodes_not_ordered

    st.session_state['funnel_nodes'] = sort_items(
        st.session_state.get('funnel_nodes_not_ordered', []))

    more_than_one_node = len(st.session_state['funnel_nodes']) > 1
    all_inputs_set = all([st.session_state['bot_id'], st.session_state['start_date'],
                         st.session_state['end_date'], more_than_one_node])
    if all_inputs_set and st.button('Update funnel'):
        update_funnel()

    if st.session_state['df'] is not None:
        st.bar_chart(st.session_state['df'], x='stage', y='value')


def update_funnel():
    funnel = get_funnel(
        bot_id=st.session_state['bot_id'],
        start_date=st.session_state['start_date'],
        end_date=st.session_state['end_date'],
        node_names=','.join(st.session_state['funnel_nodes'])
    )
    df = pd.DataFrame(funnel)
    try:
        df['stage'] = df['funnel_stage'].astype(
            str) + '-' + df['step_name']
        st.session_state['df'] = df
    except Exception as e:
        print(e)
        st.session_state['df'] = None
