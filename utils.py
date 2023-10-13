from data_lib import data_getter

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
    st.session_state['dg'] = data_getter()
    if 'init' not in st.session_state:
        st.session_state['init'] = True
        st.session_state['bot_id'] = None
        st.session_state['node_name'] = None
        st.session_state['start_date'] = None
        st.session_state['end_date'] = None
        st.session_state['dict_bot_id_nodes'] = st.session_state['dg'].get_bot_list_nodes(
        )
        st.session_state['list_nodes'] = None
        st.session_state['min_date'] = dt.datetime.strptime(
            '2023-09-12', '%Y-%m-%d')
        st.session_state['groupers_list'] = ['channel', 'language', 'country']


def main_selector():
    st.header('Multiasistencia')
    st_1, st_2, =  st.columns([3, 2])
    st_3, st_4, _, _ = st.columns([1, 1, 1, 2])

    selected_bot_id = st_1.selectbox(
        'Bot', st.session_state['dict_bot_id_nodes'].keys(), index=None, format_func=lambda x: bot_id_name_dic.get(x, x))

    if st.session_state['bot_id'] != selected_bot_id:
        st.session_state['bot_id'] = selected_bot_id
        st.session_state['node_name'] = st_2.selectbox(
            'Origin Node', st.session_state['dict_bot_id_nodes'][st.session_state['bot_id']], format_func=clean_node_names, index=None)
        st.session_state['list_nodes'] = st.session_state['dict_bot_id_nodes'][st.session_state['bot_id']]

    st.session_state['start_date'] = st_3.date_input(
        'FROM', value=today - dt.timedelta(days=21), min_value=st.session_state['min_date'], max_value=today, key=None)
    st.session_state['end_date'] = st_4.date_input(
        'TO', value=today, min_value=st.session_state['min_date'], max_value=today, key=None)

    st.session_state['start_date'] = st.session_state['start_date'].strftime(
        '%Y-%m-%d')
    st.session_state['end_date'] = st.session_state['end_date'].strftime(
        '%Y-%m-%d')


def sk_section():
    dg = st.session_state['dg']
    if st.session_state['bot_id'] and st.session_state['bot_id_has_changed']:
        st.write('SANKLEY')
        fig_sankey = dg.get_sankey_fig(bot_id=st.session_state['bot_id'],
                                       start_date=st.session_state['start_date'],
                                       end_date=st.session_state['end_date'],
                                       node_name=st.session_state['node_name'],
                                       grouper=st.session_state['grouper']
                                       )

        st.plotly_chart(fig_sankey, use_container_width=False,
                        config={'displaylogo': False})


def funnel_section():
    dg = st.session_state['dg']

    more_than_one_node = False
    nodes_has_changed = False
    if st.session_state['bot_id_has_changed'] and st.session_state['list_nodes'] and st.session_state['bot_id']:
        nodes_has_changed = nodes_funnel_selector()

    more_than_one_node = len(st.session_state['funnel_nodes_ordered']) > 1
    if more_than_one_node and nodes_has_changed and st.button('Update funnel'):
        upodate_funnel(dg, st.session_state['funnel_nodes_ordered'])

    if st.session_state['df'] is not None:
        st.bar_chart(st.session_state['df'], x='stage', y='value')


def upodate_funnel():
    dg = data_getter()
    funnel = dg.get_funnel(
        bot_id=st.session_state['bot_id'],
        start_date=st.session_state['start_date'],
        end_date=st.session_state['end_date'],
        node_names=st.session_state['funnel_nodes_ordered']
    )

    funnel_values = [f['value'] for f in funnel]
    labels = [f['step_name'] for f in funnel]
    funnel_stage = [f['funnel_stage'] for f in funnel]

    df = pd.DataFrame({
        'value': funnel_values,
        'step_name': labels,
        'funnel_stage': funnel_stage
    })
    df['stage'] = df['funnel_stage'].astype(
        str) + '-' + df['step_name']
    st.session_state['df'] = df


def nodes_funnel_selector():
    st.header('Choose your funnel steps')

    st.session_state['funnel_nodes'] = st.multiselect(
        'Funnel Nodes', st.session_state['list_nodes'], format_func=clean_node_names, max_selections=10)

    st.write("Order your funnel")
    funnel_nodes_ordered = sort_items(
        [n for n in st.session_state['funnel_nodes']])

    nodes_has_changed = st.session_state['funnel_nodes_ordered'] != funnel_nodes_ordered

    return nodes_has_changed
