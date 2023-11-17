# , get_funnel, get_handoff_top, get_path_list, get_loop_nodes
from data_lib import get_bot_list_nodes, get_sankey_fig
from figures_lib import plotly_sankey

import streamlit as st
import streamlit.components.v1 as components


import datetime as dt
from config import bot_id_name_dic

import pandas as pd
import numpy as np


def streamlit_square_color(color, size=10):
    html = f'<div style="background-color: {color}; width: {size}px; height: {size}px; border-radius: 50%; display: inline-block; margin-right: 5px;"></div>'
    return components.html(html, height=size, width=size, scrolling=False)


def clean_node_names(x):
    if x == '-':
        return 'START'
    return x.replace('_', ' ').capitalize().upper()


def st_circle_logo():
    for _ in range(4):
        st.write(' ')
    _, st_logo, _ = st.columns([3, 1, 3])
    st_logo.image('./img/ht_circle.png',
                  width=100, use_column_width=True)


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
        st.session_state['min_width'] = 1
        st.session_state['max_steps'] = None
        st.session_state['include_handoff'] = True
        st.session_state['include_no_handoff'] = True
        st.session_state['filter_out_nodes'] = None
        st.session_state['session_default'] = True
        st.session_state['number_time'] = 30
        st.session_state['time_unit'] = 'DAYS'
        st.session_state['auto_width'] = True

        nodes_set = set()
        for _, nodes_bot_id in st.session_state['dict_bot_id_nodes'].items():
            nodes_set.update(nodes_bot_id)
        st.session_state['list_nodes'] = sorted(list(nodes_set) + ['HANDOFF'])

        colors = ['rgba(167, 165, 173, 1)'] * \
            len(st.session_state['list_nodes'])
        st.session_state['color_map'] = dict(
            zip(st.session_state['list_nodes'], colors))
        st.session_state['color_map']['HANDOFF'] = 'rgba(204,53,89,1)'
        st.session_state['node_source_color'] = 'rgba(87,85,96,1)'


def update_inputs(bot_id, start_date, end_date, node_source, min_width, max_steps, include_handoff, include_no_handoff):
    if bot_id != st.session_state['bot_id'] or \
            node_source != st.session_state['node_source'] or \
            start_date != st.session_state['start_date'] or \
            end_date != st.session_state['end_date'] or \
            min_width != st.session_state['min_width'] or \
            max_steps != st.session_state['max_steps'] or \
            include_handoff != st.session_state['include_handoff'] or \
            include_no_handoff != st.session_state['include_no_handoff']:

        st.session_state['include_handoff'] = include_handoff
        st.session_state['include_no_handoff'] = include_no_handoff

        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date
        st.session_state['update_sankey'] = True
        st.session_state['start_date'] = st.session_state['start_date'].strftime(
            '%Y-%m-%d')
        st.session_state['end_date'] = st.session_state['end_date'].strftime(
            '%Y-%m-%d')
        st.session_state['max_steps'] = max_steps
        if st.session_state['bot_id'] != bot_id or st.session_state['node_source'] != node_source:
            st.session_state['bot_id'] = bot_id
            st.session_state['node_source'] = node_source
            st.session_state['min_width'] = auto_width()
            st.experimental_rerun()
        else:
            st.session_state['bot_id'] = bot_id
            st.session_state['node_source'] = node_source
            st.session_state['min_width'] = min_width

        if st.session_state['session_default'] is False:
            if st.session_state['time_unit'] == 'MINUTES':
                st.session_state['session_minutes'] = st.session_state['number_time']
            elif st.session_state['time_unit'] == 'HOURS':
                st.session_state['session_hours'] = st.session_state['number_time']
            elif st.session_state['time_unit'] == 'DAYS':
                st.session_state['session_days'] = st.session_state['number_time']
        else:
            st.session_state['session_days'] = 30


def st_header():
    st.image('./img/ht_logo.png', width=100)
    st_1, st_2 = st.columns([1, 3])
    st_1.header('Bot visualization')
    st_2.write('')
    st_2.write('')
    st_2.write('Understand how users navigate your bot')
    html_bot_setting = """
    <h2 style="font-size:18px;">Bot settings</h2>
    """
    st.markdown(html_bot_setting, unsafe_allow_html=True)


def auto_width():
    data = get_sankey_fig(bot_id=st.session_state['bot_id'],
                          start_date=st.session_state['start_date'],
                          end_date=st.session_state['end_date'],
                          node_source=st.session_state['node_source'],
                          max_steps=st.session_state['max_steps'],
                          min_width=1,
                          include_handoff=st.session_state['include_handoff'],
                          include_no_handoff=st.session_state['include_no_handoff'],
                          filter_out_nodes=st.session_state['filter_out_nodes'],
                          session_minutes=st.session_state.get(
        'session_minutes', None),
        session_hours=st.session_state.get(
        'session_hours', None),
        session_days=st.session_state.get(
        'session_days', None),
    )
    df = pd.DataFrame(data)
    df = df[df.target_order <= st.session_state['max_steps']]
    return round(df.transition_count.quantile(0.8))


def main_selector():
    st_header()

    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])

    st.session_state['list_bots'] = list(st.session_state['dict_bot_id_nodes'].keys(
    )) + ['HANDOFF'] if st.session_state['dict_bot_id_nodes'].keys() is not None else None

    bot_list = [b for b in st.session_state['list_bots']
                if b in bot_id_name_dic.keys()]
    bot_id = st_1.selectbox(
        'Bot', bot_list, index=None, format_func=lambda x: bot_id_name_dic.get(x, x))

    st.session_state['list_nodes'] = sorted(st.session_state['dict_bot_id_nodes'].get(
        bot_id, []))

    if st.session_state['list_nodes'] != []:
        list_nodes = sorted(
            st.session_state['list_nodes'] + ['HANDOFF'])
    else:
        list_nodes = []

    start_date = st_2.date_input('From', value=dt.datetime.today() - dt.timedelta(days=3),
                                 min_value=st.session_state['min_date'], max_value=dt.datetime.today(), disabled=bot_id is None)

    end_date = st_3.date_input(
        'to', value=dt.datetime.today(), min_value=st.session_state['min_date'], max_value=dt.datetime.today(), disabled=bot_id is None)

    html_bot_viz_pref = """
    <h2 style="font-size:18px;">Visualization preferences</h2>
    """
    st.markdown(html_bot_viz_pref, unsafe_allow_html=True)
    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])
    node_source = st_1.selectbox(
        'Starting node', list_nodes, format_func=clean_node_names, index=None)

    min_width = st_2.number_input(
        'Minimum nº of users in a path', value=st.session_state['min_width'], min_value=1,  disabled=(bot_id is None), help='Minimum number of users going through the same path. Increasing this helps you focus on paths that are more common. This number is AUTO CALCULATED every time you change bot or starting node.')

    max_steps = st_3.number_input(
        'Maximum nº steps', value=5, min_value=2, max_value=100, disabled=bot_id is None, help='Maximum path length (in number of steps) that you want to show')

    st_4.write('Filter paths by')
    st_h, st_n = st_4.columns([1, 1])

    include_handoff = st_h.checkbox(
        'with handoff', value=False, disabled=bot_id is None, help='This helps you filter out paths that ended  without hand off')

    include_no_handoff = st_n.checkbox(
        'no handoff', value=False, disabled=bot_id is None, help='This helps you filter out paths that ended with a handoff')

    if bot_id is None:
        st_circle_logo()
        return
    else:
        html_sesion_time = """
        <p>The parameter "end session time"  of your bot is: <b>30 days</b></p>
        """
        st.markdown(html_sesion_time, unsafe_allow_html=True)

    update_inputs(bot_id, start_date, end_date, node_source,
                  min_width, max_steps, include_handoff, include_no_handoff)


def sk_section():

    set_necessary_inputs = all(
        [st.session_state['bot_id'], st.session_state['start_date'], st.session_state['end_date'], st.session_state['min_width'], st.session_state['max_steps']])

    if set_necessary_inputs and st.session_state['update_sankey']:
        st.session_state['update_sankey'] = False

        st.session_state['sankey_data'] = get_sankey_fig(bot_id=st.session_state['bot_id'],
                                                         start_date=st.session_state['start_date'],
                                                         end_date=st.session_state['end_date'],
                                                         node_source=st.session_state['node_source'],
                                                         max_steps=st.session_state['max_steps'],
                                                         min_width=st.session_state['min_width'],
                                                         include_handoff=st.session_state['include_handoff'],
                                                         include_no_handoff=st.session_state['include_no_handoff'],
                                                         filter_out_nodes=st.session_state['filter_out_nodes'],
                                                         session_minutes=st.session_state.get(
                                                             'session_minutes', None),
                                                         session_hours=st.session_state.get(
                                                             'session_hours', None),
                                                         session_days=st.session_state.get(
                                                             'session_days', None),
                                                         )

        try:
            fig_main, fig_nodes = plotly_sankey(
                st.session_state['sankey_data'])
            st.plotly_chart(fig_nodes,
                            config={
                                'staticPlot':  True,
                            }
                            )
            st.plotly_chart(fig_main,
                            use_container_width=True,
                            config={
                                'displaylogo': False,
                            }
                            )
        except Exception as e:
            st_circle_logo()
            _, st_1, _ = st.columns([6, 2, 6])
            st_1.warning('No data available')
            st.write(str(e))


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
