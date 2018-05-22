import logging

from flask import Flask
from .extensions import cors, rest_api
from . import views, commands
# from server import views, commands
# from config.settings import settings


def create_app(config_object=None):
    app = Flask(__name__.split('.')[0])
    # app.config.from_object(config_object)
    # app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://" + settings['POSTGRES_USER'] + ":" + \
    #     settings['POSTGRES_PASSWORD'] + '@' + settings['POSTGRES_HOST'] + ':5432/' + settings['POSTGRES_DB']
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def register_extensions(app):
    # db.init_app(app)
    cors.init_app(app)
    rest_api.init_app(app)

    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(views.blueprint)

    return None


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.create_all)
    app.cli.add_command(commands.drop_all)
    app.cli.add_command(commands.init)
    app.cli.add_command(commands.set_admin_credentials)


