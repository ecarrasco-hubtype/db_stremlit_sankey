import plotly.graph_objects as go
import pandas as pd
import numpy as np


def assign_linspace(group):
    group.sort_values('incoming_sum', inplace=True, ascending=True)
    group['y'] = (group['incoming_sum']/2).iloc[::-1].cumsum()[::-1]
    group['y'] = group['y'] / group['y'].max()
    return group.reset_index(drop=True)


def plotly_sankey(data, max_path_len=None, n_filter=1, title="Sankey Diagram", ):

    df = pd.DataFrame(data)

    # Filter data_flow with transitions less than n_filter
    df = df[df['transition_count'] >= n_filter]

    # filter maxlen path by sufix in string las 3 chars
    df = df[df['target_order'] <= max_path_len]

    pd.options.mode.chained_assignment = None  # default='warn'

    df_labels = pd.concat([df[['source_node', 'source_order']].rename(columns={'source_node': 'node', 'source_order': 'order'}), df[[
                          'target_node', 'target_order']].rename(columns={'target_node': 'node', 'target_order': 'order'})]).drop_duplicates()
    df_labels = df_labels.reset_index().rename(columns={'index': 'i_label'})
    df_labels['incoming_sum'] = df_labels.apply(lambda row: df[(df.target_node == row.node) & (
        df.target_order == row.order)].transition_count.sum(), axis=1)

    df_labels['nodes_per_stage'] = df_labels.groupby(
        'order').node.transform('count')
    df_labels['vertical_order'] = df_labels.groupby('order').incoming_sum.transform(
        lambda x: x.rank(ascending=False, method='dense'))

    df_labels['x'] = (df_labels['order'] - 1) / df_labels['order'].max()

    pd.options.mode.chained_assignment = 'warn'

    df_labels = df_labels.groupby('order').apply(
        assign_linspace).reset_index(drop=True)
    # df_labels['y'] = df_labels['y']/df_labels['y'].max()

    df['i_source'] = df.apply(lambda row: df_labels[(df_labels.node == row.source_node) & (
        df_labels.order == row.source_order)].index[0], axis=1)
    df['i_target'] = df.apply(lambda row: df_labels[(df_labels.node == row.target_node) & (
        df_labels.order == row.target_order)].index[0], axis=1)

    sankey = go.Sankey(
        # arrangement="perpendicular",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=df_labels['node'].values,
            color="#491291",
            x=df_labels['x'].values,
            y=df_labels['y'].values,
        ),
        link=dict(
            arrowlen=30,
            source=df['i_source'].values,
            target=df['i_target'].values,
            value=df['transition_count'].values,
            color="#F6F6F6",
        ))

    fig = go.Figure(data=[sankey])
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    if title != '':
        fig.update_layout(title_text=title, font_size=10)
    return fig
