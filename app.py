from config import bot_id_name_dic
import datetime as dt
import pandas as pd
from data_lib import data_getter
import streamlit as st
from streamlit_sortables import sort_items


from utils import clean_node_names

import importlib
import data_lib
importlib.reload(data_lib)


dg = data_getter()
if 'init' not in st.session_state:
    st.session_state['init'] = True
    st.session_state['bot_id'] = None
    st.session_state['node_name'] = None
    st.session_state['list_nodes'] = None
    st.session_state['start_date'] = None
    st.session_state['end_date'] = None
    st.session_state['list_bot_ids'] = dg.get_bot_list()
    st.session_state['min_date'] = dt.datetime.strptime(
        '2023-09-12', '%Y-%m-%d')
    st.session_state['groupers_list'] = ['channel', 'language', 'country']

today = dt.datetime.today()

st.header('Multiasistencia')
st_1, st_2, =  st.columns([3, 2])
st_3, st_4, _, st_5 = st.columns([1, 1, 1, 2])


selected_bot_id = st_1.selectbox(
    'Bot', st.session_state['list_bot_ids'], index=None, format_func=lambda x: bot_id_name_dic.get(x, x))
if selected_bot_id != st.session_state['bot_id']:
    st.session_state['bot_id'] = selected_bot_id
    st.session_state['list_nodes'] = dg.get_node_list(
        st.session_state['bot_id'])

if st.session_state['bot_id'] != None:
    st.session_state['node_name'] = st_2.selectbox(
        'Origin Node', st.session_state['list_nodes'], format_func=clean_node_names, index=None)
    st.session_state['grouper'] = st_5.selectbox(
        'Group by', st.session_state['groupers_list'], index=None, format_func=lambda x: x.capitalize())

st.session_state['start_date'] = st_3.date_input(
    'FROM', value=today - dt.timedelta(days=7), min_value=st.session_state['min_date'], max_value=today, key=None)

st.session_state['end_date'] = st_4.date_input(
    'TO', value=today, min_value=st.session_state['min_date'], max_value=today, key=None)

if st.session_state['bot_id'] != None:
    fig_sankey = dg.get_sankey_fig(bot_id=st.session_state['bot_id'],
                                   start_date=st.session_state['start_date'].strftime(
                                       '%Y-%m-%d'),
                                   end_date=st.session_state['end_date'].strftime(
                                       '%Y-%m-%d'),
                                   node_name=st.session_state['node_name'],
                                   grouper=st.session_state['grouper']
                                   )

    st.plotly_chart(fig_sankey, use_container_width=False,
                    config={'displaylogo': False})


if st.session_state['list_nodes']:
    st.header('Choose your funnel steps')

    st.session_state['funnel_nodes'] = st.multiselect(
        'Funnel Nodes', st.session_state['list_nodes'], format_func=clean_node_names, max_selections=10)

    st.write("Order your funnel")
    st.session_state['funnel_nodes_ordered'] = sort_items(
        [clean_node_names(n) for n in st.session_state['funnel_nodes']])

    if st.button('Update funnel') and len(st.session_state['funnel_nodes']) > 1:

        bot_id = st.session_state['bot_id']
        start_date = st.session_state['start_date'].strftime('%Y-%m-%d')
        end_date = st.session_state['end_date'].strftime('%Y-%m-%d')
        node_names = st.session_state['funnel_nodes_ordered']

        funnel = dg.get_funnel(
            bot_id=bot_id,
            start_date=start_date,
            end_date=end_date,
            node_names=','.join(node_names)
        )

        funnel_values = [f['value'] for f in funnel]
        labels = [f['step_name'] for f in funnel]
        df = pd.DataFrame(funnel)
        df['stage'] = df['funel_stage'].astype(
            str) + '-' + df['step_name']
        st.bar_chart(df, x='stage', y='value')
