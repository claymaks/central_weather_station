from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import server, db

migrate = Migrate(server, db)
manager = Manager(server)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    #heroku run python manage.py db upgrade --app name_of_your_application
    manager.run()