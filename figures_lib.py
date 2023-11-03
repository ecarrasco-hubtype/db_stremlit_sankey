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
            0: 'rgba(204, 53, 89, 0.2)',
            1: 'rgba(110, 73, 255, 0.2)',
            2: 'rgba(167, 165, 173, 0.2)'})
    return df, df_nodes


def plotly_sankey(data):

    df, df_nodes = pandas_from_sankey_data(data)
    if df is None or df_nodes is None:
        return None

    # Nodes colore
    df_nodes['node_color'] = df_nodes['node'].map(
        st.session_state['color_map'])

    if st.session_state['node_source'] is not None and st.session_state['node_source'] != 'HANDOFF':
        df_nodes.loc[(df_nodes['node'] == st.session_state['node_source']) & (df_nodes['order'] == 1),
                     'node_color'] = st.session_state['node_source_color']

    # Legends data
    legends_data = []
    if not st.session_state['include_handoff'] and not st.session_state['include_no_handoff']:
        legends_data += [
            ('rgba(0, 0, 0, 0.2)', "all paths", 'legend1')
        ]

    else:
        if st.session_state['include_handoff']:
            legends_data += (
                'rgba(110, 73, 255, 0.8)', "with handoff", 'legend1'
            ),

        if st.session_state['include_no_handoff']:
            legends_data += (
                'rgba(255, 187, 203, 0.5)', "no handoff", 'legend1'
            ),

    if st.session_state['node_source'] is not None and st.session_state['node_source'] != 'HANDOFF':
        legends_data += [
            ('rgba(87,85,96,1)', "First node", "legend2"),
        ]

    legends_data += [
        ('rgba(110,73,255,1)', "Handoff node", "legend2"),
    ]

    # Markers legend
    legends = []
    for color, name, legend in legends_data:
        legends.append(
            go.Scatter(
                mode="markers",
                x=[None],
                y=[None],
                marker=dict(size=10, color=color, symbol="square"),
                name=name,
                legend=legend,
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
        ))
    ]

    traces = sankey + legends
    fig = go.Figure(data=traces,
                    layout=dict(
                        # showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.1,
                            xanchor="center",
                            x=0.1),

                        legend1=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.1,
                            xanchor="center",
                            x=0.85),

                        legend2=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.1,
                            xanchor="center",
                            x=0.5),

                        hoverlabel=dict(
                            font=dict(color='rgba(87,85,96,1)'),
                        )
                    )
                    )

    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
