from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_restful import Api

db = SQLAlchemy()
cors = CORS()
rest_api = Api()