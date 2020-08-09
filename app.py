import flask
from flask import request

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

from db.api import get_temp_data, insert_data

import csv
import time
import datetime

server = flask.Flask(__name__)

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
                        html.H4("INSIDE/OUTSIDE TEMPERATURE DIFFERENTIAL", className="app__header__title"),
                        html.P(
                            "Temperature taken from two DHT11 Temperature and Huminity sensors, one outside my window, and one in my room.",
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
                            [html.H6("TEMPERATURE (ºF)", className="graph__title")]
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
                                            "Temperature Difference",
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
                                            "HUMIDITY", className="graph__title"
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
    if len(df) > 0:
        return df
    else:
        return [0]


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

    df = get_temp_data("TEMPERATURE", time.time()- 60*60*24 - 60*30, time.time() + 60*30)
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x))),
        df['ID']))
    inside_graph = dict(
        type="scatter",
        x=X,
        y=df['INSIDE'],
        line={"color": "#42C4F7", "name":"Inside Temperature"},
        hoverinfo="x+y",
        mode="lines",
        name="Inside Temperature"
    )

    outside_graph = dict(
        type="scatter",
        x=X,
        y=df['OUTSIDE'],
        line={"color": "#FF5733", "name":"Outside Temperature"},
        hoverinfo="x+y",
        mode="lines",
        name="Outside Temperature"
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
            "range": list(map(lambda x: datetime.datetime.fromtimestamp(x), value)),
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
    Output("humidity", "figure"), [Input("temperature-update", "n_intervals")]
)
def humidity(interval):
    """
    Generate the humidity graph.
    :params interval: update the graph based on an interval
    """
    df = get_temp_data("HUMIDITY", time.time()- 60*60*24 - 60*30, time.time() + 60*30)
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x))),
        df['ID']))
    


    humidity_out_graph = dict(
        type="scatter",
        x=X,
        y=df["OUTSIDE"],
        line={"color": "#F7C842", "width":1},
        hoverinfo="x+y",
        mode="lines",
        name="Outside Humidity"
    )

    humidity_in_graph = dict(
        type="scatter",
        x=X,
        y=df["INSIDE"],
        line={"color": "#42F797", "width":.5},
        hoverinfo="x+y",
        mode="lines",
        name="Inside Humidity"
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=350,
        xaxis={
            "range": [datetime.datetime.now() - datetime.timedelta(0, 60*60*2),
                        datetime.datetime.now() + datetime.timedelta(0, 60*60)],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "title": "Datetime",
        },
        yaxis={
            "range": [min(min(slen(df['INSIDE'])), min(slen(df['OUTSIDE']))) - 5,
                      max(max(slen(df['INSIDE'])), max(slen(df['OUTSIDE']))) + 5],
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
    [Input("temperature-update", "n_intervals")]
)
def gen_dif(interval):
    """
    Genererate wind histogram graph.
    :params interval: upadte the graph based on an interval
    """
    df = get_temp_data("TEMPERATURE", time.time()- 60*60*24 - 60*30, time.time() + 60*30)
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x))),
        df['ID']))

    dif_graph = dict(
        type="scatter",
        x=X,
        y=df["DIF"],
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
            "range": [datetime.datetime.now() - datetime.timedelta(0, 60*60*2),
                        datetime.datetime.now() + datetime.timedelta(0, 60*60)],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "title": "Datetime",
        },
        yaxis={
            "range": [min(slen(df["DIF"])) - 5,
                      max(slen(df["DIF"])) + 5],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 6
        },
    )

    return dict(data=[dif_graph], layout=layout)


@server.route("/add-data/<string:table>", methods=["GET", "POST", "PUT"])
def add_data(table):
    print(f"[{table}]")
    for dt, inside, outside in zip(request.json['dt'],
                                 request.json['inside'],
                                 request.json['outside']):
        print(f"\t{dt}: {inside} {outside}")
        insert_data(table.upper(), dt, float(inside), float(outside))
    return ''


if __name__ == "__main__":
    app.run_server(port=5000, debug=False)

