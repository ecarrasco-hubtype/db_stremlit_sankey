import plotly.graph_objects as go


def plotly_sankey(labels, title = "Basic Sankey Diagram", source = None, target = None, value = None):

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = labels,
        color = "blue"
        ),
        link = dict(
        source = source,
        target = target,
        value = value
    ))])

    fig.update_layout(title_text= title, font_size=10)
    return fig