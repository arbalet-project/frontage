import os


settings = {}

settings['POSTGRES_USER'] = os.environ['POSTGRES_USER']
settings['POSTGRES_PASSWORD'] = os.environ['POSTGRES_PASSWORD']
settings['POSTGRES_DB'] = os.environ['POSTGRES_DB']
settings['POSTGRES_HOST'] = os.environ['POSTGRES_HOST']