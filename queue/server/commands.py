"""Click commands."""
import os
import click
from db.base import session_factory, Base, engine
from db.models import FappModel, ConfigModel, DimensionsModel, DisabledPixelsModel

from utils.security import hash_password
from apps import get_app_names
from getpass import getpass
from flask.cli import with_appcontext
from apps import *

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, 'tests')


@click.command()
@with_appcontext
def create_all():
    return _create_all()

def _create_all():
    click.echo('Initialization of database...')
    Base.metadata.create_all(engine)
    initiate_db_config()
    initiate_db_fapp()
    initiate_db_dimensions()

@click.command()
@with_appcontext
def drop_all():
    """Initialize the database."""
    click.echo('Dropping the db...')
    Base.metadata.drop_all()

@click.command()
@with_appcontext
def init():
    click.echo('Initialization of Arbalet backend...')
    _create_all()
    _set_admin_credentials()

@click.command()
def set_admin_credentials():
    return _set_admin_credentials()

def _set_admin_credentials():
    session = session_factory()
    conf = session.query(ConfigModel).first()
    click.echo("Please choose your admin password (More than 8 characters, space-free)...")

    while True:
        login = input("Admin login: ")
        if len(login) < 4:
            click.echo("Admin username must contain at least 4 characters")
        elif login != login.strip():
            click.echo("Admin username cannot start or end with spaces")
        else:
            break

    while True:
        password = getpass("Admin password:")

        if len(password) < 8:
            click.echo("Password must contain at least 8 characters")
        elif password != password.strip():
            click.echo("Password cannot start or end with spaces")
        else:
            password2 = getpass("Retype password:")
            if password != password2:
                click.echo("Passwords do not match")
            else:
                break


    conf.admin_login = login
    conf.admin_hash = hash_password(password)
    session.commit()
    session.close()
    click.echo("Backend initialized")

@click.command()
def clean():
    """Remove *.pyc and *.pyo files recursively starting at current directory.
    Borrowed from Flask-Script, converted to use Click.
    """
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                full_pathname = os.path.join(dirpath, filename)
                click.echo('Removing {}'.format(full_pathname))
                os.remove(full_pathname)

def initiate_db_dimensions():
    session = session_factory()
    conf = session.query(DimensionsModel).first()
    if not conf:
        height, width = -1, -1
        while True:
            height_in = input("Enter height (number of rows): ")
            width_in = input("Enter width (number of columns): ")
            try:
                height = int(height_in)
                width = int(width_in)
            except:
                pass
            if height > 0 and width > 0:
                break
            else:
                click.echo("Invalid dimensions, please retry")
        conf = DimensionsModel(height, width)
        session.add(conf)

        # Adding optional disabled pixels (inexisting pixels)
        num_disabled = 0
        while True:
            click.echo("{} pixels have been disabled so far".format(num_disabled))
            answer = input("Is there any {}disabled pixel? [y/N] ".format("other " if num_disabled > 0 else ""))
            if answer in ['y', 'Y']:
                row, col = -1, -1
                row_in = input("Enter disabled pixel's row: ")
                col_in = input("Enter disabled pixel's column: ")
                try:
                    row = int(row_in)
                    col = int(col_in)
                except:
                    pass
                if row < 0 or col < 0:
                    click.echo("Invalid pixel, please retry")
                else:
                    dis_pix = DisabledPixelsModel(row, col)
                    session.add(dis_pix)
                    click.echo("Pixel ({}, {}) has been disabled".format(row, col))
                    num_disabled += 1
            else:
                break
        
        if num_disabled > 0:
            click.echo("{} pixels have been disabed in total".format(num_disabled))
        else:
            click.echo("No pixel have been disabed")

    session.commit()
    session.close()

def initiate_db_config():
    session = session_factory()
    conf = session.query(ConfigModel).first()

    if not conf:
        click.echo("No configuration found, initiating config creation...")
        conf = ConfigModel()
        session.add(conf)

    session.commit()
    session.close()

def initiate_db_fapp():
    session = session_factory()
    db_apps = session.query(FappModel).all()
    db_apps_names = [x.name for x in db_apps]
    apps = get_app_names()

    for fap in apps:
        # not in db ? We create the fapp
        if fap not in db_apps_names:
            scheduled = not globals()[fap].PLAYABLE
            click.echo("Creating app {} (scheduled = {})...".format(fap, scheduled))
            db_fap = FappModel(fap, is_scheduled=scheduled)
            session.add(db_fap)
    session.commit()
    session.close()
