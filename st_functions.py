# , get_funnel, get_handoff_top, get_path_list, get_loop_nodes
from data_lib import get_bot_list_nodes, get_sankey_fig
from figures_lib import plotly_sankey

import streamlit as st
import streamlit.components.v1 as components

import plotly.express as px

import datetime as dt
from config import bot_id_name_dic


today = dt.datetime.today()


def streamlit_square_color(color, size=10):
    html = f'<div style="background-color: {color}; width: {size}px; height: {size}px; border-radius: 50%; display: inline-block; margin-right: 5px;"></div>'
    return components.html(html, height=size, width=size, scrolling=False)


def clean_node_names(x):
    if x == '-':
        return 'START'
    return x.replace('_', ' ').capitalize().upper()


def st_circle_logo_message(message='🤖 SELECT A BOT TO START 🚀'):
    for _ in range(3):
        st.header(' ')
    _, st_logo, _ = st.columns([11, 4, 11])
    st_logo.image('./img/ht_circle.png',
                  width=70, use_column_width=True)
    st_logo.success(message)


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
        st.session_state['min_width'] = 1100
        st.session_state['max_steps'] = None
        st.session_state['include_handoff'] = True
        st.session_state['include_no_handoff'] = True
        st.session_state['filter_out_nodes'] = None
        st.session_state['session_default'] = True
        st.session_state['number_time'] = 30
        st.session_state['time_unit'] = 'DAYS'
        nodes_set = set()
        for _, nodes_bot_id in st.session_state['dict_bot_id_nodes'].items():
            nodes_set.update(nodes_bot_id)
        st.session_state['list_nodes'] = sorted(list(nodes_set) + ['HANDOFF'])
        colors = px.colors.qualitative.Plotly * \
            (round(len(st.session_state['list_nodes']
                       )/len(px.colors.qualitative.Plotly)) + 2)

        colors = ['#7964CC', '#736A99', '#6E4AFF',
                  '#4D34B3', '#5F40DB', '#3B288A', '#2A1C61'] * 50
        st.session_state['color_map'] = dict(
            zip(st.session_state['list_nodes'], colors))
        st.session_state['color_map']['HANDOFF'] = '#FF4AC6'


def main_selector():

    st_1, st_2 = st.columns([2, 3])
    st_l, st_r = st_1.columns([1, 2])
    st_l.write(' ')
    st_l.write(' ')
    st_l.image('./img/ht_logo.png', width=100)

    st_r.title('Bot visualization')

    st_2.write(' ')
    st_2.write(' ')
    st_2.write('Understand users navigate your bors')

    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])

    st.session_state['list_bots'] = list(st.session_state['dict_bot_id_nodes'].keys(
    )) + ['HANDOFF'] if st.session_state['dict_bot_id_nodes'].keys() is not None else None

    bot_list = [b for b in st.session_state['list_bots']
                if b in bot_id_name_dic.keys()]
    bot_id = st_1.selectbox(
        'BOT', bot_list, index=None, format_func=lambda x: bot_id_name_dic.get(x, x))

    st.session_state['list_nodes'] = sorted(st.session_state['dict_bot_id_nodes'].get(
        bot_id, []))

    if st.session_state['list_nodes'] != []:
        list_nodes = sorted(
            st.session_state['list_nodes'] + ['HANDOFF'])
    else:
        list_nodes = []

    start_date = st_2.date_input('FROM', value=today - dt.timedelta(days=30),
                                 min_value=st.session_state['min_date'], max_value=today, disabled=bot_id is None)

    end_date = st_3.date_input(
        'TO', value=today, min_value=st.session_state['min_date'], max_value=today, disabled=bot_id is None)

    st.write('Visualization preferences')
    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])
    node_source = st_1.selectbox(
        'STARTING NODE', list_nodes, format_func=clean_node_names, index=None)
    min_width = st_2.number_input(
        'MIN. USERS PATH', value=1, min_value=1, max_value=10000, disabled=bot_id is None)
    max_steps = st_3.number_input(
        'MAX. NUMBER STEPS', value=5, min_value=2, max_value=100, disabled=bot_id is None)

    st_4.write('Filter paths by')
    st_h, st_n = st_4.columns([1, 1])

    include_handoff = st_h.checkbox(
        'HANDOFF', value=False, disabled=bot_id is None)

    include_no_handoff = st_n.checkbox(
        'NO HANDOFF', value=False, disabled=bot_id is None)
    # Filter out nodes tool
    # filter_out_nodes = st_2.multiselect('FILTER OUT NODES', list_nodes,
    #                                     format_func=clean_node_names, max_selections=99, help="Exclude nodes from the graph bypassing them")

    # Change session time
    # session_default = st.checkbox(
    #     'DEFAULT', value=True, disabled=bot_id is None)
    # number_time = st.number_input(
    #     'NUMBER', value=30, min_value=1, max_value=10000, disabled=session_default)
    # time_unit = st.selectbox(
    #     'UNIT', ['MINUTES', 'HOURS', 'DAYS'], index=2, disabled=session_default)

    if bot_id is None:
        st_circle_logo_message()
        return

    if bot_id != st.session_state['bot_id'] or \
            node_source != st.session_state['node_source'] or \
            start_date != st.session_state['start_date'] or \
            end_date != st.session_state['end_date'] or \
            min_width != st.session_state['min_width'] or \
            max_steps != st.session_state['max_steps'] or \
            include_handoff != st.session_state['include_handoff'] or \
            include_no_handoff != st.session_state['include_no_handoff']:
        # session_default != st.session_state['session_default'] or \
        # number_time != st.session_state['number_time'] or \
        # time_unit != st.session_state['time_unit']
        # or \ filter_out_nodes != st.session_state['filter_out_nodes']:

        # st.session_state['filter_out_nodes'] = filter_out_nodes
        # st.session_state['session_default'] = session_default
        # st.session_state['number_time'] = number_time
        # st.session_state['time_unit'] = time_unit
        st.session_state['include_handoff'] = include_handoff
        st.session_state['include_no_handoff'] = include_no_handoff
        st.session_state['bot_id'] = bot_id
        st.session_state['node_source'] = node_source
        st.session_state['start_date'] = start_date
        st.session_state['end_date'] = end_date
        st.session_state['update_sankey'] = True
        st.session_state['start_date'] = st.session_state['start_date'].strftime(
            '%Y-%m-%d')
        st.session_state['end_date'] = st.session_state['end_date'].strftime(
            '%Y-%m-%d')
        st.session_state['min_width'] = min_width
        st.session_state['max_steps'] = max_steps

        if st.session_state['session_default'] is False:
            if st.session_state['time_unit'] == 'MINUTES':
                st.session_state['session_minutes'] = st.session_state['number_time']
            elif st.session_state['time_unit'] == 'HOURS':
                st.session_state['session_hours'] = st.session_state['number_time']
            elif st.session_state['time_unit'] == 'DAYS':
                st.session_state['session_days'] = st.session_state['number_time']
        else:
            st.session_state['session_days'] = 30


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
            st.plotly_chart(plotly_sankey(st.session_state['sankey_data'],
                                          title='',
                                          ),
                            use_container_width=True,
                            config={
                'displaylogo': False}
            )
        except Exception as e:
            st_circle_logo_message(message=str(e))  # "NO DATA FOUND")


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
