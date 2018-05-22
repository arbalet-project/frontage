import datetime

# from server.extensions import db
from uuid import uuid4
from db.base import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean


def cln_str(s):
    if s:
        return s.replace(
            "'",
            "").replace(
            '\\',
            '').replace(
            '%',
            '').replace(
                ';',
            '')
    return ''


class FappModel(Base):
    __tablename__ = 'fapp'

    uniqid = Column(String(36), primary_key=True)
    name = Column(String(36), unique=True)
    is_scheduled = Column(Boolean)
    default_params = Column(String(36))
    position = Column(Integer)
    duration = Column(Integer)
    created_at = Column(DateTime, unique=False)

    def __init__(self, app_name, is_scheduled=False):
        self.uniqid = str(uuid4())
        self.position = 0
        self.duration = (15 * 60)
        self.name = app_name
        self.is_scheduled = is_scheduled
        self.default_params = '{}'
        self.created_at = datetime.datetime.now()

    def __repr__(self):
        return '<Fapp %r (%r) (%r) (%r)>' % (
            self.uniqid, self.is_scheduled, self.position, self.default_params)


class ConfigModel(Base):
    __tablename__ = 'configmodel'

    uniqid = Column(String(36), primary_key=True)

    forced_sunrise = Column(String(36))
    offset_sunrise = Column(Integer)

    forced_sunset = Column(String(36))
    offset_sunset = Column(Integer)
    state = Column(String(36))
    expires_delay = Column(Integer)
    default_app_lifetime = Column(Integer)

    admin_login = Column(String(36))
    admin_hash = Column(String(512))

    def __init__(self):
        self.uniqid = str(uuid4())
        self.forced_sunset = ""
        self.offset_sunset = 0
        self.state = 'scheduled'

        self.forced_sunrise = ""
        self.offset_sunrise = 0
        self.default_app_lifetime = 15 * 60

        self.expires_delay = 90

    def __repr__(self):
        return '<ConfigModel %r (%r) (%r)>' % (
            self.uniqid, self.expires_delay, self.forced_sunset)
