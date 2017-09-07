import redis

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Config
app.config['SERVER_HOST'] = '127.0.0.1'
app.debug = True
# Redis setup
try:
	redis = redis.StrictRedis(host=app.config['SERVER_HOST'])
	redis.ping()
except Exception as e:
	raise

# Loading views.py
import views