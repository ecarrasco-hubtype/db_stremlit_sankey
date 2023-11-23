# , get_funnel, get_handoff_top, get_path_list, get_loop_nodes
from data_lib import get_bot_list_nodes, get_sankey_fig, get_bot_id_name_from_org_id

import streamlit as st
import streamlit.components.v1 as components

from figures_lib import plotly_sankey

import datetime as dt
from config import email_company_dic
import texts
import config
import pandas as pd
import re


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


def get_user_email():
    email_from_user = st.experimental_user.get('email')
    if not email_from_user:
        return None

    match = re.search(r'@([a-zA-Z0-9.-]+)', str(email_from_user))

    if not match:
        return None

    dominio = match.group(1).lower()
    return dominio


def get_dicc_org_id_from_user():
    if st.session_state['email_company'] is None:
        return None
    return email_company_dic.get(st.session_state['email_company'], None)


def init_st():
    if 'init' not in st.session_state:
        st.set_page_config(layout="wide")
        st.session_state['init'] = True
        st.session_state['email_company'] = get_user_email()
        st.session_state['dict_company_name_id'] = get_dicc_org_id_from_user()
        st.session_state['company_name'] = list(
            st.session_state['dict_company_name_id'].keys())[0]
        st.session_state['company_id'] = st.session_state['dict_company_name_id'].get(
            st.session_state['company_name'], None)

        st.session_state['dict_bot_name_id'] = get_bot_id_name_from_org_id(
            st.session_state['company_id'])
        st.session_state['dict_bot_id_nodes'] = get_bot_list_nodes(
            st.session_state['company_id'])

        st.session_state['min_date'] = dt.datetime.strptime(
            '2023-09-12', '%Y-%m-%d')

        st.session_state['min_width'] = 1
        st.session_state['include_handoff'] = True
        st.session_state['include_no_handoff'] = True
        st.session_state['session_default'] = True
        st.session_state['auto_width'] = True


def update_inputs(bot_id, start_date, end_date, node_source, min_width, max_steps, include_handoff, include_no_handoff, company_name):
    session_state = st.session_state

    if session_state.get('company_name', None) != company_name:
        session_state['company_name'] = company_name
        session_state['org_id'] = session_state['dict_company_name_id'].get(
            company_name, None)
        session_state['dict_bot_name_id'] = get_bot_id_name_from_org_id(
            session_state['org_id'])
        session_state['dict_bot_id_nodes'] = get_bot_list_nodes(
            session_state['org_id'])
        st.rerun()

    if session_state.get('bot_id', None) != bot_id or session_state.get('node_source', None) != node_source:
        session_state['bot_id'] = bot_id
        session_state['node_source'] = node_source
        session_state['min_width'] = auto_width()
        st.rerun()

    session_state['bot_id'] = bot_id
    session_state['node_source'] = node_source
    session_state['min_width'] = min_width
    session_state['include_handoff'] = include_handoff
    session_state['include_no_handoff'] = include_no_handoff
    session_state['start_date'] = start_date.strftime('%Y-%m-%d')
    session_state['end_date'] = end_date.strftime('%Y-%m-%d')
    session_state['update_sankey'] = True
    session_state['max_steps'] = max_steps


def st_header():
    st_1, st_2, st_3, st_4 = st.columns([1, 2, 6, 3])
    st_1.write('')
    st_1.write('')
    st_1.image('./img/ht_logo.png', width=100)

    st_2.header(texts.main_title)
    st_3.write('')
    st_3.write('')
    st_3.write(texts.sub_title)

    st_4.write(st.session_state['email_company'])
    # html_bot_setting = """
    # <h2 style="font-size:18px;">Bot settings</h2>
    # """
    # st.markdown(html_bot_setting, unsafe_allow_html=True)


def auto_width():
    data = get_sankey_fig(bot_id=st.session_state['bot_id'],
                          start_date=st.session_state['start_date'],
                          end_date=st.session_state['end_date'],
                          node_source=st.session_state.get(
                              'node_source', None),
                          max_steps=st.session_state['max_steps'],
                          min_width=1,
                          include_handoff=st.session_state.get(
                              'include_handoff', None),
                          include_no_handoff=st.session_state.get(
                              'include_no_handoff', None),
                          filter_out_nodes=st.session_state.get(
                              'filter_out_nodes', None),
                          )
    try:
        df = pd.DataFrame(data)
        df = df[df.target_order <= st.session_state['max_steps']]
        return round(df.transition_count.quantile(config.auto_width_quantile))
    except Exception:
        return 1


def main_selector():
    st_header()
    session_state = st.session_state
    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])
    company_name = st_4.selectbox(
        'Company', list(session_state['dict_company_name_id'].keys()), format_func=lambda x: x.upper())
    bot_name = st_1.selectbox(
        'Bot', session_state['dict_bot_name_id'].keys(), index=None, format_func=lambda x: x.upper())
    bot_id = session_state['dict_bot_name_id'].get(bot_name, None)

    session_state['list_nodes'] = session_state['dict_bot_id_nodes'].get(
        bot_id, [])
    if session_state['list_nodes'] != [] and 'HANDOFF' not in session_state['list_nodes']:
        session_state['list_nodes'] += ['HANDOFF']
        session_state['list_nodes'] = sorted(session_state['list_nodes'])

    start_date = st_2.date_input('From', value=dt.datetime.today() - dt.timedelta(days=7),
                                 min_value=session_state['min_date'], max_value=dt.datetime.today(), disabled=bot_id is None)

    end_date = st_3.date_input(
        'to', value=dt.datetime.today(), min_value=session_state['min_date'], max_value=dt.datetime.today(), disabled=bot_id is None)

    # html_bot_viz_pref = """
    # <h2 style="font-size:18px;">Visualization preferences</h2>
    # """
    # st.markdown(html_bot_viz_pref, unsafe_allow_html=True)
    st_1,  st_2, st_3, st_4 = st.columns(
        [1, 1, 1, 1])
    no_bot_selected = 'bot_id' not in session_state
    node_source = st_1.selectbox(
        'Starting node', session_state.get('list_nodes', None), format_func=clean_node_names, index=None, disabled=no_bot_selected, help=texts.tooltip_starting_node)

    min_width = st_2.number_input(
        'Minimum nº of users in a path', value=session_state['min_width'], min_value=1,  disabled=(bot_id is None), help=texts.tooltip_min_width)

    max_steps = st_3.number_input(
        'Maximum nº steps', value=5, min_value=2, max_value=100, disabled=bot_id is None, help=texts.tooltip_max_steps)

    st_4.write('Filter paths by')
    st_h, st_n = st_4.columns([1, 1])

    include_handoff = st_h.checkbox(
        'with handoff', value=False, disabled=bot_id is None, help=texts.tooltip_include_handoff)

    include_no_handoff = st_n.checkbox(
        'no handoff', value=False, disabled=bot_id is None, help=texts.tooltip_include_no_hanoff)

    update_inputs(bot_id, start_date, end_date, node_source,
                  min_width, max_steps, include_handoff, include_no_handoff, company_name)
    if session_state['bot_id'] is None:
        st_circle_logo()
        return
    else:
        html_sesion_time = f"""
        <p>{texts.session_time}<b>30 days</b></p>
        """
        st.markdown(html_sesion_time, unsafe_allow_html=True)


def sk_section():
    session_state = st.session_state
    set_necessary_inputs = all(
        [session_state['bot_id'], session_state['start_date'], session_state['end_date'], session_state['min_width'], session_state['max_steps']])

    if set_necessary_inputs and session_state['update_sankey']:
        session_state['update_sankey'] = False

        session_state['sankey_data'] = get_sankey_fig(bot_id=session_state['bot_id'],
                                                      start_date=session_state['start_date'],
                                                      end_date=session_state['end_date'],
                                                      node_source=session_state.get(
                                                          'node_source', None),
                                                      max_steps=session_state['max_steps'],
                                                      min_width=session_state.get(
                                                          'min_width', 1),
                                                      include_handoff=session_state.get(
                                                          'include_handoff', None),
                                                      include_no_handoff=session_state.get(
                                                          'include_no_handoff', None),
                                                      filter_out_nodes=session_state.get(
                                                          'filter_out_nodes', None),
                                                      session_minutes=session_state.get(
            'session_minutes', None),
            session_hours=session_state.get(
            'session_hours', None),
            session_days=session_state.get(
            'session_days', None),
        )

        try:
            fig_main, fig_nodes = plotly_sankey(
                session_state['sankey_data'])
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
            st_1.warning(texts.no_data)
            # st.write(str(e))
