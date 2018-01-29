from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# local import
from instance.config import Config


# initialize sql-alchemy
db = SQLAlchemy()


def create_app():
    """
    Creates our flask app

    Returns:
        Flask
    """
    from app.models import Guest
    from app.resources import GuestsList, GuestsAPI, TwilioResponseAPI

    app = Flask(__name__, instance_relative_config=True)
    config = Config()
    app.config.from_object(config)
    app.logger.debug("Config loaded {}".format(config))
    db.init_app(app)

    # flask-restful
    api = Api(app)

    api.add_resource(GuestsAPI,
                     '/api/guest',
                     '/api/guest/<int:guest_id>',
                     resource_class_kwargs={'guest_object': Guest},
                     endpoint="guest-api")
    api.add_resource(GuestsList,
                     '/api/guests',
                     resource_class_kwargs={'guest_object': Guest},
                     endpoint="guest-list")
    api.add_resource(TwilioResponseAPI,
                     '/api/sms',
                     resource_class_kwargs={'guest_object': Guest},
                     endpoint="sms")


    # Create admin
    admin = Admin(app, name='Wedding Reply Site', template_mode='bootstrap3')

    # Add views
    admin.add_view(ModelView(Guest, db.session))

    return app
