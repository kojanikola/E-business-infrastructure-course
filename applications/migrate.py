from flask import Flask
from configuration1 import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import db, Razlog
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, db);

done = False

while not done:
    try:
        if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"])

        db.init_app(application)
        with application.app_context() as context:
            init();
            migrate(message="Production migration")
            upgrade();

            duplicateBallot = Razlog(tip="Duplicate ballot.")
            invalidPollNumber = Razlog(tip="Invalid poll number.")

            db.session.add(duplicateBallot)
            db.session.add(invalidPollNumber)
            db.session.commit()
            done = True
    except Exception as error:
        print(error)
