from app import server, db
from app.models import *
from app.dashboard import *
from flask import request
import numpy as np

import time

@server.route("/get-data/<string:table>", methods=["GET"])
def get_data(table):
    df = []
    if table == "temperature":
        df = Temperature.query.filter((Temperature.dt >= 0) & (Temperature.dt <= int(time.time()))).all()
    elif table == "humidity":
        df = Humidity.query.filter((Humidity.dt >= 0) & (Humidity.dt <= int(time.time()))).all()
    print(f"[{table}]")
    return {'data': list(map(lambda x: (x.id, x.dt, x.inside, x.outside, x.dif), df))}


@server.route("/add-data/<string:table>", methods=["POST"])
def add_data(table, json=None):
    print(f"[{table}]")
    json = json or request.json
    for dt, inside, outside in zip(json['dt'],
                                   json['inside'],
                                   json['outside']):
        print(f"\t{dt}: {inside} {outside}")

        if table == "temperature":
            data = Temperature(dt, inside, outside, outside - inside)
            db.session.add(data)
            db.session.commit()
        elif table == "humidity":
            data = Humidity(dt, inside, outside, outside - inside)
            db.session.add(data)
            db.session.commit()

    return ''


@server.route("/delete-data/<string:table>/<int:_id>", methods=["DELETE"])
def delete_data(table, _id):
    deleted = False
    if table == "temperature" and Temperature.query.get(_id):
        db.session.delete(Temperature.query.get(_id))
        deleted = True
    elif table == "humidity" and Humidity.query.get(_id):
        db.session.delete(Humidity.query.get(_id))
        deleted = True
    db.session.commit()
    return {'deleted': deleted, 'table': table, 'id': _id}


@server.route("/delete-data/<string:table>/<int:strt>/<int:end>", methods=["DELETE"])
def batch_delete_data(table, strt, end):
    deleted = []
    for _id in range(strt, end):
        deleted.append(delete_data(table, _id)['deleted'])
    return {'deleted': deleted, 'table': table, 'ids': list(range(strt, end))}


@server.route("/condense/", methods=["PUT"])
def condense(sz=4500, interval=50):
    temp = Temperature.query.filter((Temperature.dt >= 0) & (Temperature.dt <= int(time.time()))).all()
    temp_df = np.array(list(map(lambda x: (x.id, x.dt, x.inside, x.outside, x.dif), temp)))
    temp_df = temp_df.T[1:]
    
    new_temp = []
    for i in range(0,sz, interval):
        arr = temp_df[:,i:i+interval]
        new_temp.append(np.sum(arr, axis=1)/interval)
    new_temp = np.array(new_temp).T
    print("condensed temperature")
    add_data("temperature", json={'dt': new_temp[0], 'inside': new_temp[1], 'outside': new_temp[2]})
    print("added")


    humid = Humidity.query.filter((Humidity.dt >= 0) & (Humidity.dt <= int(time.time()))).all()
    humid_df = np.array(list(map(lambda x: (x.id, x.dt, x.inside, x.outside, x.dif), humid)))
    humid_df = humid_df.T[1:]
    
    new_humid = []
    for i in range(0,sz, interval):
        arr = humid_df[:,i:i+interval]
        new_humid.append(np.sum(arr, axis=1)/interval)
    new_humid = np.array(new_humid).T
    print("condensed humidity")
    add_data("humidity", json={'dt': new_humid[0], 'inside': new_humid[1], 'outside': new_humid[2]})
    print("added")
    
    return ''
    
    
    
                          
