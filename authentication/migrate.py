from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, migrate, upgrade
from models import db, Role, UserRole, User
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

            adminRole = Role(name="Admin")
            userRole = Role(name="Izborni zvanicnik")

            db.session.add(adminRole)
            db.session.add(userRole)
            db.session.commit()

            admin = User(
                email="admin@admin.com",
                password="1",
                ime="admin",
                prezime="admin",
                jmbg="0000000000000"
            )

            db.session.add(admin);
            db.session.commit();

            userRole = UserRole(
                userId=admin.id,
                roleId=adminRole.id
            );

            db.session.add(userRole);
            db.session.commit()

            done = True
    except Exception as error:
        print(error)
