from app import server, db
from app.models import *
from app.dashboard import *
from flask import request

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
def add_data(table):
    print(f"[{table}]")
    for dt, inside, outside in zip(request.json['dt'],
                                   request.json['inside'],
                                   request.json['outside']):
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


@server.route("/delete-data/<int:_id>/<string:table>", methods=["DELETE"])
def delete_data(_id, table):
    deleted = False
    if table == "temperature" and Temperature.query.get(_id):
        db.session.delete(Temperature.query.get(_id))
        deleted = True
    elif table == "humidity" and Humidity.query.get(_id):
        db.session.delete(Humidity.query.get(_id))
        deleted = True
    return {'deleted': deleted, 'table': table, 'id': _id}
                          
