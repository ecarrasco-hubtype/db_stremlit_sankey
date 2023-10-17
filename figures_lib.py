import plotly.graph_objects as go


def plotly_sankey(data, max_path_len=None, n_filter=1, title="Sankey Diagram", ):
    # Filter data_flow with transitions less than n_filter
    data = [d for d in data
            if d['transition_count'] >= n_filter]

    # filter maxlen path by sufix in string las 3 chars
    if max_path_len is not None:
        data = [d for d in data
                if int(d['target_action'][-3:]) <= max_path_len]

    labels = list(set([d['source_action']
                  for d in data] + [d['target_action'] for d in data]))

    value = [d['transition_count'] for d in data]
    target = [labels.index(d['target_action']) for d in data]
    source = [labels.index(d['source_action']) for d in data]

    sankey = go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color="#491291"
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color="#F6F6F6",
        ))

    fig = go.Figure(data=[sankey])
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    if title != '':
        fig.update_layout(title_text=title, font_size=10)
    return fig
