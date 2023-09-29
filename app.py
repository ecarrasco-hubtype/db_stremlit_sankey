import streamlit as st
from data_lib import data_getter
import load_dotenv
import os
load_dotenv.load_dotenv()
import datetime as dt

dg = data_getter()
list_bot_ids = dg.get_bot_list()
min_date = dt.datetime.strptime('2023-09-12 00:00:00', '%Y-%m-%d %H:%M:%S')
today= dt.datetime.today()

st.header('Multiasistencia')
st_l, st_c, st_r = st.columns([3, 1, 1 ])
bot_id = st_l.selectbox('Select bot', list_bot_ids)
start_date = st_c.date_input('From: ', value=today - dt.timedelta(days=15), min_value=min_date, max_value=today, key=None)
end_date = st_r.date_input('To: ', value=today, min_value=min_date, max_value=today, key=None)
if bot_id : st_l.write(f'Bot selected: {bot_id}')

sankey = dg.get_sankey_fig(bot_id, dt.datetime.strftime(start_date, '%Y-%m-%d 00:00:00'), dt.datetime.strftime(end_date, '%Y-%m-%d 00:00:00'))
st.plotly_chart(sankey, use_container_width=True)