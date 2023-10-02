import plotly.graph_objects as go
import plotly.colors as colors

palette = colors.qualitative.Plotly


def plotly_sankey(labels, title = "Basic Sankey Diagram", source = None, target = None, value = None, grouper = None):  
    color_map = None
    if grouper:
        color_map = {k: palette[i] for i, k in enumerate(set(grouper))}
        color = [color_map[k] for k in grouper]
    else:
        color = "#F6F6F6"



    sankey = go.Sankey(
                                        node = dict(
                                        pad = 15,
                                        thickness = 20,
                                        line = dict(color = "black", width = 0.5),
                                        label = labels,
                                        color = "#491291"
                                        ),
                                        link = dict(
                                        source = source,
                                        target = target,
                                        value = value,
                                        color = color,
                                        ))


    if color_map:
        legend = []
        lengend_entries = [[v,k] for k,v in color_map.items()]
        for entry in lengend_entries:
            legend.append(
                go.Scatter(
                    mode="markers",
                    x=[None],
                    y=[None],
                    marker=dict(size=10, color=entry[0], symbol="square"),
                    name=entry[1],
                )
            )

    traces = [sankey] + legend if color_map else [sankey]
    layout = go.Layout(
                        showlegend=True,
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
    fig = go.Figure(data=traces, layout=layout)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig