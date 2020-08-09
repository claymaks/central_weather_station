import flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go

#from db.api import get_temp_data, insert_data

import os
import csv
import time
import datetime

server = flask.Flask(__name__)
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'postgresql://localhost/weather')
heroku = Heroku(server)
db = SQLAlchemy(server)

class Temperature(db.Model):
    __tablename__ = "temperature"
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.Integer)
    inside = db.Column(db.Float)
    outside = db.Column(db.Float)
    dif = db.Column(db.Float)
    
    
    def __init__(self, dt, inside, outside, dif):
        self.dt = dt
        self.inside = inside
        self.outside = outside
        self.dif = dif

    def __repr__(self):
        return f"TEMPERATURE {self.dt}: {self.outside} - {self.inside} = {self.dif}"


class Humidity(db.Model):
    __tablename__ = "humidity"
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.Integer)
    inside = db.Column(db.Float)
    outside = db.Column(db.Float)
    dif = db.Column(db.Float)
    
    
    def __init__(self, dt, inside, outside, dif):
        self.dt = dt
        self.inside = inside
        self.outside = outside
        self.dif = dif

    def __repr__(self):
        return f"HUMIDITY {self.dt}: {self.outside} - {self.inside} = {self.dif}"
    
        
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
    df = db.session.query(Temperature).filter((Temperature.dt >= value[0]) & (Temperature.dt <= value[1])).all()
    inside = list(map(lambda x: x.inside, df))
    outside = list(map(lambda x: x.outside, df))
    
    X = list(map(
        lambda x: datetime.datetime.fromtimestamp(time.mktime(time.gmtime(x.dt))),
        df))
    inside_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.inside, df)),
        line={"color": "#42C4F7", "name":"Inside Temperature"},
        hoverinfo="x+y",
        mode="lines",
        name="Inside Temperature"
    )

    outside_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.outside, df)),
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
    df = db.session.query(Humidity).filter((Humidity.dt >= value[0]) & (Humidity.dt <= value[1])).all()
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
        name="Outside Humidity"
    )

    humidity_in_graph = dict(
        type="scatter",
        x=X,
        y=list(map(lambda x: x.inside, df)),
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
    df = db.session.query(Temperature).filter((Temperature.dt >= value[0]) & (Temperature.dt <= value[1])).all()
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


@server.route("/get-data/<string:table>", methods=["GET"])
def get_data(table):
    df = db.session.query(Temperature).filter((Temperature.dt >= 0) & (Temperature.dt <= int(time.time()))).all()
    print(f"[{table}]")
    return {'data': list(map(lambda x: (x.id, x.dt, x.inside, x.outside, x.dif), df))}

@server.route("/add-data/<string:table>", methods=["POST"])
def add_data(table):
    print(f"[{table}]")
    for dt, inside, outside in zip(request.json['dt'],
                                 request.json['inside'],
                                 request.json['outside']):
        print(f"\t{dt}: {inside} {outside}")
        
        if table == "temperature":
            data = Temperature(dt, inside, outside, outside-inside)
            db.session.add(data)
            db.session.commit()
        elif table == "humidity":
            data = Humidity(dt, inside, outside, outside-inside)
            db.session.add(data)
            db.session.commit()

        
    return ''


if __name__ == "__main__":
    app.run_server(port=5000, debug=False)

