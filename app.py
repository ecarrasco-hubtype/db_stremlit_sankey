import streamlit as st

import importlib
import data_lib
importlib.reload(data_lib)
from data_lib import data_getter

import datetime as dt

dg = data_getter()
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state['bot_id'] = None
    st.session_state['node_name'] = None
    st.session_state['list_nodes'] = None
    st.session_state['start_date'] = None
    st.session_state['end_date'] = None
    st.session_state['list_bot_ids'] = dg.get_bot_list()
min_date = dt.datetime.strptime('2023-09-12 00:00:00', '%Y-%m-%d %H:%M:%S')
today= dt.datetime.today()

st.header('Multiasistencia')
st_1, st_2, st_3 =  st.columns([3, 2, 1 ])
_,_, st_4 = st.columns([3, 2, 1 ])


selected_bot_id = st_1.selectbox('Bot',st.session_state['list_bot_ids'], index=st.session_state['list_bot_ids'].index(st.session_state['bot_id']) if st.session_state['bot_id'] else 0)

if selected_bot_id != st.session_state['bot_id']:
    st.session_state['bot_id'] = selected_bot_id
    st.session_state['list_nodes'] = dg.get_node_list(st.session_state['bot_id'])


st.session_state['node_name'] = st_2.selectbox('Origin Node',st.session_state['list_nodes'], index=st.session_state['list_nodes'].index(st.session_state['node_name']) if st.session_state['node_name'] else 0)


start_date = st_3.date_input('FROM', value=today - dt.timedelta(days=7), min_value=min_date, max_value=today, key=None)
end_date = st_4.date_input('TO', value=today, min_value=min_date, max_value=today, key=None)
st.session_state['start_date'] = start_date.strftime('%Y-%m-%d 00:00:00')
st.session_state['end_date'] = end_date.strftime('%Y-%m-%d 00:00:00')

fig_sankey = dg.get_sankey_fig( bot_id = st.session_state['bot_id'],
                                start_date = st.session_state['start_date'],
                                end_date = st.session_state['end_date'],
                                node_name = st.session_state['node_name']
                            )
st.plotly_chart(fig_sankey, use_container_width=True, config={'displaylogo': False})
