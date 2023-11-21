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
    k = 2
    df_nodes['y_cum'] = df_nodes['node_volume'] / 2 + \
        df_nodes.groupby('order').node_volume.transform(
            lambda x: x.cumsum().shift(1).fillna(0)) * k

    df_nodes['volume_per_order'] = df_nodes.groupby(
        'order')['node_volume'].transform('sum')

    # df_nodes['y'] = df_nodes['y_cum'] / (df_nodes['volume_per_order'])
    df_nodes['y'] = df_nodes['y_cum'] / (df_nodes['y_cum'].max())

    df_nodes = df_nodes.reset_index(drop=True).reset_index(
        drop=False).rename(columns={'index': 'i_node'})

    df['i_source'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'source_node', 'source_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)
    df['i_target'] = df.merge(df_nodes[['node', 'order', 'i_node']], how='left', left_on=[
        'target_node', 'target_order'], right_on=['node', 'order'], suffixes=('', '_node'))['i_node'].fillna(-1).astype(int)

    df['color'] = df['session_with_handoff'].map(
        {
            0: 'rgba(110, 73, 255, 0.2)',
            1: 'rgba(204, 53, 89, 0.2)',
            2: 'rgba(167, 165, 173, 0.2)'})
    return df, df_nodes


def plotly_sankey(data):

    df, df_nodes = pandas_from_sankey_data(data)
    if df is None or df_nodes is None:
        return None
    df_nodes['node_color'] = st.session_state['color_regular_node']

    if st.session_state['node_source'] is not None:
        df_nodes.loc[(df_nodes['node'] == st.session_state['node_source']) & (df_nodes['order'] == 1),
                     'node_color'] = st.session_state['color_source_node']

    df_nodes.loc[df_nodes['node'] == 'HANDOFF',
                 'node_color'] = st.session_state['color_handoff_node']

    legends_paths = []
    if not st.session_state['include_handoff'] and not st.session_state['include_no_handoff']:
        legends_paths += [
            ('rgba(165, 165, 173, 0.2)', "all", 'Paths', 'arrow-right'),
        ]

    else:
        if st.session_state['include_handoff']:
            legends_paths += (
                'rgba(204, 53, 89, 0.2)', "with handoff", 'Paths', 'arrow-right'
            ),

        if st.session_state['include_no_handoff']:
            legends_paths += (
                'rgba(110, 73, 255, 0.2)', "without handoff", 'Paths', 'arrow-right'
            ),

    legends_nodes = [
        ('rgba(204,53,89,1)', "Handoff", "Nodes", 'square'),
        ('rgba(167, 165, 173, 1)', "Regular ", "Nodes", 'square'),

    ]
    if st.session_state['node_source'] is not None and st.session_state['node_source'] != 'HANDOFF':
        legends_nodes += [
            ('rgba(87,85,96,1)', "Starting", "Nodes", 'square'),
        ]

    # Markers legend
    traces_paths = []
    for color, name, legend_group, symbol in legends_paths:
        traces_paths.append(
            go.Scatter(
                mode="markers",
                x=[None],
                y=[None],
                marker=dict(color=color, symbol=symbol, size=20),
                name=name,
                legendgrouptitle=dict(text=legend_group),
                legendgroup=legend_group,
            )
        )
    traces_nodes = []
    for color, name, legend_group, symbol in legends_nodes:
        traces_nodes.append(
            go.Scatter(
                mode="markers",
                x=[None],
                y=[None],
                marker=dict(color=color, symbol=symbol, size=15),
                name=name,
            )
        )

    sankey = [go.Sankey(
        # arrangement="perpendicular",
        # arrangement="snap",
        node=dict(
            pad=5,
            thickness=30,
            line=dict(color="white", width=3),
            label=df_nodes['node'].values,
            color=df_nodes['node_color'].values,
            x=df_nodes['x'].values,
            y=df_nodes['y'].values,
            customdata=np.stack(
                (df_nodes['order'], df_nodes['node_volume']), axis=-1),
            hovertemplate='TRAFFIC: <b>%{customdata[1]}</b><br>ORDER: %{customdata[0]}<extra></extra>',

        ),
        link=dict(
            arrowlen=30,
            source=df['i_source'].values,
            target=df['i_target'].values,
            value=df['transition_count'].values,
            color=df['color'].values,
            line=dict(width=1, color='rgba(255, 255, 255, 0.7)'),
            customdata=np.stack((df['session_with_handoff'].map(
                {0: 'no handoff', 1: 'handoff', 2: 'all paths'}
            ),  df['transition_count']), axis=-1),
            hovertemplate='<br><b>FROM</b>: %{source.label}<br><b>TO</b>: %{target.label}<br><br>TRAFFIC: <b>%{customdata[1]}</b><b><extra>%{customdata[0]}</b></extra>',
        )
    )
    ]

    traces_main = sankey + traces_paths
    layout_paths = go.Layout(
        dict(
            showlegend=True,
            legend=dict(
                orientation="v",
                y=1.3,
                x=0.95,
            ),

            hoverlabel=dict(
                font=dict(color='rgba(39,38,43,1)'),
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=500
        )
    )

    fig_main = go.Figure(data=traces_main,
                         layout=layout_paths

                         )

    fig_main.update_xaxes(visible=False)
    fig_main.update_yaxes(visible=False)

    layout_nodes = go.Layout(
        dict(
            showlegend=True,
            legend=dict(
                orientation="h",
                y=1.3,
                x=0.02,
            ),

            hoverlabel=dict(
                font=dict(color='rgba(39,38,43,1)'),
            )
        )
    )
    fig_nodes = go.Figure(data=traces_nodes,
                          layout=layout_nodes
                          )

    fig_nodes.update_xaxes(visible=False)
    fig_nodes.update_yaxes(visible=False)
    fig_nodes.update_layout(
        height=100,  # Alto en píxeles
    )
    return fig_main, fig_nodes
