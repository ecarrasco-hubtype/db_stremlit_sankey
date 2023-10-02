import streamlit as st

import importlib
import data_lib
importlib.reload(data_lib)
from data_lib import data_getter

import datetime as dt

from config import bot_id_name_dic

dg = data_getter()
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state['bot_id'] = None
    st.session_state['node_name'] = None
    st.session_state['list_nodes'] = None
    st.session_state['start_date'] = None
    st.session_state['end_date'] = None
    st.session_state['list_bot_ids'] = dg.get_bot_list()
    st.session_state['min_date'] = dt.datetime.strptime('2023-09-12 00:00:00', '%Y-%m-%d %H:%M:%S')
    st.session_state['groupers_list'] = ['channel', 'language', 'country']

today= dt.datetime.today()

st.header('Multiasistencia')
st_1, st_2, =  st.columns([3, 2 ])
st_3, st_4,_, st_5 = st.columns([1, 1,1, 2 ])


selected_bot_id = st_1.selectbox('Bot',st.session_state['list_bot_ids'], index=None, format_func=lambda x: bot_id_name_dic.get(x, x))
if selected_bot_id != st.session_state['bot_id']:
    st.session_state['bot_id'] = selected_bot_id
    st.session_state['list_nodes'] = dg.get_node_list(st.session_state['bot_id'])

if st.session_state['bot_id'] != None:
    st.session_state['node_name'] = st_2.selectbox('Origin Node',st.session_state['list_nodes'], format_func=lambda x: str.replace(x, '_', ' ').capitalize().replace('-', 'START'), index=None)
    st.session_state['grouper'] = st_5.selectbox('Group by', st.session_state['groupers_list'], index = None, format_func=lambda x: x.capitalize())

st.session_state['start_date'] = st_3.date_input('FROM', value=today - dt.timedelta(days=7), min_value=st.session_state['min_date'], max_value=today, key=None).strftime('%Y-%m-%d 00:00:00')
st.session_state['end_date'] = st_4.date_input('TO', value=today, min_value=st.session_state['min_date'], max_value=today, key=None).strftime('%Y-%m-%d 00:00:00')

if st.session_state['bot_id'] != None:
    fig_sankey = dg.get_sankey_fig( bot_id = st.session_state['bot_id'],
                                    start_date = st.session_state['start_date'],
                                    end_date = st.session_state['end_date'],
                                    node_name = st.session_state['node_name'],
                                    grouper = st.session_state['grouper']
                                )

    st.plotly_chart(fig_sankey, use_container_width=False, config={'displaylogo': False})
