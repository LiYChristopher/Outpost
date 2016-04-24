#!usr/bin/env python
import os

# WTF
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = os.urandom(24)
SECRET_KEY = os.urandom(24)

# MongoEngine
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

# Flask-Cache
CACHE_TYPE = 'filesystem'
CACHE_DEFUALT_TIMEOUT = 30
CACHE_DIR = os.path.join(os.path.abspath('blog'), 'tmp')

DOWNLOAD_DIR = os.path.join(os.path.abspath('blog'), 'static', 'downloadable')
# Flask-Uploads
UPLOADED_PHOTOS_DEST = os.path.join(os.path.abspath('blog'), 'static', 'uploads')
UPLOADED_PHOTOS_DIR = '/static/uploads'
UPLOADED_FILES_ALLOW = set(['jpg', 'png', 'gif', 'jpeg'])
UPLOADED_FILES_DENY = set(['doc', 'docx', 'xml', 'yaml',
	                       'yml', 'rc', 'ini', 'csv',
	                       'json', 'txt', 'rtf'])
