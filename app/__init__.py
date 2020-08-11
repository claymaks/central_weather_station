import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_heroku import Heroku
from config import Config

server = flask.Flask(__name__)
server.config.from_object(Config)

db = SQLAlchemy(server)
migrate = Migrate(server, db)

heroku = Heroku(server)

from app import models, routes
