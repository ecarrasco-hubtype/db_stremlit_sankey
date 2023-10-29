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
    df_nodes['x'] = (df_nodes['order'] - 1) / \
        (df_nodes['order'].max()) + 1/(2*df_nodes['order'].max())

    df_nodes = df_nodes.sort_values(
        ['order', 'node_volume'], ascending=[True, False])

    # k_space_nodes_percetange
    k = 1 + 0.2
    df_nodes['y_cum'] = df_nodes['node_volume'] / 2 + \
        df_nodes.groupby('order').node_volume.transform(
            lambda x: x.cumsum().shift(1).fillna(0)) * k

    df_nodes['volume_per_order'] = df_nodes.groupby(
        'order')['node_volume'].transform('sum')

    df_nodes['y'] = df_nodes['y_cum'] / (df_nodes['volume_per_order'])
    # df_nodes['y'] = df_nodes['y_cum'] / (df_nodes['y_cum'].max())

    df_nodes = df_nodes.reset_index(drop=True).reset_index(
        drop=False).rename(columns={'index': 'i_node'})

    df['i_source'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'source_node', 'source_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)
    df['i_target'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'target_node', 'target_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)

    df['color'] = df['session_with_handoff'].map(
        {0: 'rgba(110, 73, 255, 0.4)', 1: 'rgba(110, 73, 255, 0.8)'})

    return df, df_nodes


def plotly_sankey(data, title="Sankey Diagram", ):

    df, df_nodes = pandas_from_sankey_data(data)
    if df is None or df_nodes is None:
        return None

    sankey = go.Sankey(
        # arrangement="perpendicular",
        # arrangement="snap",
        node=dict(
            pad=5,
            thickness=30,
            line=dict(color="white", width=1.5),
            label=df_nodes['node'].values,
            color=df_nodes['node'].map(
                st.session_state['color_map']).to_list(),
            x=df_nodes['x'].values,
            y=df_nodes['y'].values,
            customdata=np.stack((df_nodes['order'], df_nodes['node_volume'],
                                 df_nodes['x'], df_nodes['y']), axis=-1),
            hovertemplate='TRAFFIC: <b>%{customdata[1]}</b><br>ORDER: %{customdata[0]}<br>X: %{customdata[2]:.2f},<br>Y: %{customdata[3]:.2f}<extra></extra>',
        ),
        link=dict(
            arrowlen=30,
            source=df['i_source'].values,
            target=df['i_target'].values,
            value=df['transition_count'].values,
            color=df['color'].values,
            line=dict(width=1, color='rgba(110, 74, 255, 0.2)'),
            customdata=np.stack((df['session_with_handoff'].map(
                {0: 'NO HANDOFF', 1: 'HANDOFF'}),  df['transition_count']), axis=-1),
            hovertemplate='<br>FROM: %{source.label}<br>TO: %{target.label}<br>TRAFFIC: <b>%{customdata[1]}<br><br>%{customdata[0]}</b><extra></extra>',
        ))
    fig = go.Figure(data=[sankey])

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    if title != '':
        fig.update_layout(title_text=title, font_size=10)

    return fig
