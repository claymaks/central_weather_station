import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import server, db


server.config.from_object('config.ProductionConfig')

migrate = Migrate(server, db)
manager = Manager(server)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
