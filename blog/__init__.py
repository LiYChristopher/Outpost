''' Flask is instantiated here, as are the extensions we will be using
which include:
	- Flask-Login
	- Flask-Misaka
	- Flask-Uploads
	- Flask-Cache
'''
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.uploads import UploadSet, IMAGES
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from flask.ext.misaka import Misaka


app = Flask(__name__)
db = MongoEngine()

app.config['MONGODB_DB'] = 'chris_blog'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017

# extensions
login_manager = LoginManager()
md = Misaka(space_headers=True, no_intra_emphasis=True, fenced_code=True)
photos = UploadSet('photos', IMAGES)
cache = Cache()

from blog import views, forms
