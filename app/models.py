from app import db

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
        return f"temperature {self.dt}: {self.outside} - {self.inside} = {self.dif}"


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
        return f"humidity {self.dt}: {self.outside} - {self.inside} = {self.dif}"