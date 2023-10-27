import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st


def pandas_from_sankey_data(data):

    df = pd.DataFrame(data)
    if len(df) == 0:
        return None, None
    df_targets = df[['target_node', 'target_order',
                    'target_node_incoming']].drop_duplicates()
    df_targets.columns = ['node', 'order', 'node_volume']

    df_sorces = df[['source_node', 'source_order',
                    'source_node_outcoming']].drop_duplicates()
    df_sorces.columns = ['node', 'order', 'node_volume']

    df_nodes = pd.concat(
        [df_targets, df_sorces[df_sorces.order == 1]]).drop_duplicates()

    df_nodes['x'] = (df_nodes['order'] - 1) / (df_nodes['order'].max()+1)
    df_nodes['x'] = 0.9 * df_nodes['x']/df_nodes['x'].max()

    df_nodes['y_cumsum'] = df_nodes.groupby(
        'order')['node_volume'].transform(lambda v: v.sort_values(ascending=False).cumsum().shift(1).fillna(0))

    df_nodes['y'] = df_nodes.y_cumsum + df_nodes.node_volume / 2
    df_nodes['y'] = df_nodes.y / df_nodes.y.max()

    df_nodes = df_nodes.reset_index(drop=True).reset_index(
        drop=False).rename(columns={'index': 'i_node'})

    df['i_source'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'source_node', 'source_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)
    df['i_target'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'target_node', 'target_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)

    df['color'] = df['session_with_handoff'].map(
        {0: 'rgba(246, 246, 246, 0.8)', 1: 'rgba(211, 211, 211, 0.8)'})

    return df, df_nodes


def plotly_sankey(data, title="Sankey Diagram", ):

    df, df_nodes = pandas_from_sankey_data(data)
    if df is None or df_nodes is None:
        return None

    sankey = go.Sankey(
        # arrangement="perpendicular",
        arrangement="snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=df_nodes['node'].values,
            color=df_nodes['node'].map(
                st.session_state['color_map']).to_list(),
            x=df_nodes['x'].values,
            y=df_nodes['y'].values,
            customdata=np.stack((df_nodes['order'], df_nodes['node_volume'],
                                 df_nodes['x'], df_nodes['y']), axis=-1),
            hovertemplate='NODE: %{label}<br>TRAFFIC: %{customdata[1]}<br>ORDER: %{customdata[0]}<br>X: (%{customdata[2]:.2f},<br>Y: %{customdata[3]:.2f})',
        ),
        link=dict(
            arrowlen=30,
            source=df['i_source'].values,
            target=df['i_target'].values,
            value=df['transition_count'].values,
            color=df['color'].values,
            line=dict(width=0.5, color='rgba(0,0,0, 0.5)'),
            hovertemplate='FROM: %{source.label}<br>TO: %{target.label}<br> TRAFFIC: %{value}',
        ))

    fig = go.Figure(data=[sankey])

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    if title != '':
        fig.update_layout(title_text=title, font_size=10)

    return fig
