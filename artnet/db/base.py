from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from db.settings import settings


engine = create_engine("postgresql+psycopg2://" + settings['POSTGRES_USER'] + ":" +
                       settings['POSTGRES_PASSWORD'] + '@' + settings['POSTGRES_HOST'] + ':5432/' + settings['POSTGRES_DB'])
# use session_factory() to get a new Session
_SessionFactory = sessionmaker(bind=engine)
Base = declarative_base(bind=engine)

def session_factory():
    return _SessionFactory()
