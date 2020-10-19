from app import server, db
from app.models import *

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

import time
import datetime

app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/',
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

GRAPH_INTERVAL = 5000 # clientside update
app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(
    [
        # header
        html.Div(
            [
                html.Div(
                    [
                        html.H4("INSIDE/OUTSIDE temperature DIFFERENTIAL", className="app__header__title"),
                        html.P(
                            "temperature taken from two DHT11 temperature and Huminity sensors, one outside my window, and one in my room.",
                            className="app__header__title--grey",
                        ),
                    ],
                    className="app__header__desc",
                ),
            ],
            className="app__header",
        ),
        html.Div(
            [
                # temperatures
                html.Div(
                    [
                        html.Div(
                            [html.H6("temperature (ºF)", className="graph__title")]
                        ),
                        dcc.RangeSlider(
                            id='my-range-slider',
                            min=time.mktime(datetime.datetime(2020,8,8).timetuple()),
                            max=time.mktime(datetime.datetime.now().timetuple()),
                            value=[time.mktime((datetime.datetime.now() - datetime.timedelta(1)).timetuple()),
                                   time.mktime(datetime.datetime.now().timetuple())],
                        ),

                        html.Div([
                            html.P(
                                "dt - dt",
                                id="range-info",
                                className="auto__p",
                                )
                        ],
                        className="auto__container"),
                        
                        dcc.Graph(
                            id="temperature",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="temperature-update",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ),
                    ],
                    className="two-thirds column wind__speed__container",
                    # className="two-thirds column temperature__container",
                ),
                html.Div(
                    [
                        # dif
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "temperature Difference",
                                            className="graph__title",
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="dif-line",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container first",
                        ),
                        # humidity
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "humidity", className="graph__title"
                                        )
                                    ]
                                ),
                                dcc.Graph(
                                    id="humidity",
                                    figure=dict(
                                        layout=dict(
                                            plot_bgcolor=app_color["graph_bg"],
                                            paper_bgcolor=app_color["graph_bg"],
                                        )
                                    ),
                                ),
                            ],
                            className="graph__container second",
                        ),
                    ],
                    className="one-third column histogram__direction",
                ),
            ],
            className="app__content",
        ),
    ],
    className="app__container",
)

def slen(df):
    if not df or len(df) == 0:
        return [0]
    return df


@app.callback(
    Output("range-info", "children"),
    [Input("my-range-slider", "value")]
)
def update_range(value):
    return datetime.datetime.strftime(datetime.datetime.fromtimestamp(value[0]), "%a %b %d %H:%M:%S %Y") + ' - ' + datetime.datetime.strftime(datetime.datetime.fromtimestamp(value[1]), "%a %b %d %H:%M:%S %Y")


@app.callback(
    Output("temperature", "figure"),
    [Input("temperature-update", "n_intervals"),
     Input("my-range-slider", "value")]
)
def gen_temp(interval, value):
    """
    Generate the temperature graph.
    :params interval: update the graph based on an interval
    """
    df = Temperature.query.filter((Temperature.dt >= value[0]) & (Temperature.dt <= value[1])).all()
    print(len(df))
    inside = list(map(lambda x: x.inside, df))
    outside = list(map(lambda x: x.outside, df))
    
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x.dt))),
        df))
    inside_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.inside, df)),
        line={"color": "#42C4F7", "name":"Inside temperature"},
        hoverinfo="x+y",
        mode="lines",
        name="Inside temperature"
    )

    outside_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.outside, df)),
        line={"color": "#FF5733", "name":"Outside temperature"},
        hoverinfo="x+y",
        mode="lines",
        name="Outside temperature"
    )
    
    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=700,
        xaxis={
            "range": list(map(lambda x: datetime.datetime.fromtimestamp(x), value)),
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "title": "Datetime",
        },
        yaxis={
            "range": [min(min(slen(inside)), min(slen(outside))) - 5,
                      max(max(slen(inside)), max(slen(outside))) + 5],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 6
        },
    )

    return dict(data=[inside_graph, outside_graph], layout=layout)


@app.callback(
    Output("humidity", "figure"),
    [Input("temperature-update", "n_intervals"),
     Input("my-range-slider", "value")]
)
def humidity(interval, value):
    """
    Generate the humidity graph.
    :params interval: update the graph based on an interval
    """
    df = Humidity.query.filter((Humidity.dt >= value[0]) & (Humidity.dt <= value[1])).all()
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x.id))),
        df))
    inside = list(map(lambda x: x.inside, df))
    outside = list(map(lambda x: x.outside, df))


    humidity_out_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.outside, df)),
        line={"color": "#F7C842", "width":1},
        hoverinfo="x+y",
        mode="lines",
        name="Outside humidity"
    )

    humidity_in_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.inside, df)),
        line={"color": "#42F797", "width":.5},
        hoverinfo="x+y",
        mode="lines",
        name="Inside humidity"
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=350,
        xaxis={
            "range": list(map(lambda x: datetime.datetime.fromtimestamp(x), value)),
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "title": "Datetime",
        },
        yaxis={
            "range": [min(min(slen(inside)), min(slen(outside))) - 5,
                      max(max(slen(inside)), max(slen(outside))) + 5],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 6
        },
    )

    return dict(data=[humidity_out_graph, humidity_in_graph], layout=layout)


@app.callback(
    Output("dif-line", "figure"),
    [Input("temperature-update", "n_intervals"),
     Input("my-range-slider", "value")]
)
def gen_dif(interval, value):
    """
    Genererate wind histogram graph.
    :params interval: upadte the graph based on an interval
    """
    df = Temperature.query.filter((Temperature.dt >= value[0]) & (Temperature.dt <= value[1])).all()
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x.dt))),
        df))
    
    dif_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.dif, df)),
        line={"color": "#F7E942", "width":1},
        hoverinfo="x+y",
        mode="lines",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=350,
        xaxis={
            "range": list(map(lambda x: datetime.datetime.fromtimestamp(x), value)),
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "title": "Datetime",
        },
        yaxis={
            "range": [min(slen(list(map(lambda x: x.dif, df)))) - 5,
                      max(slen(list(map(lambda x: x.dif, df)))) + 5],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 6
        },
    )

    return dict(data=[dif_graph], layout=layout)
