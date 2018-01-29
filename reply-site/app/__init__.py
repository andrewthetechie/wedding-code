from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

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
    return app
