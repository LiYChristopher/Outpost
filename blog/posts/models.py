''' Post and Post data related models and helper functions. '''
from blog import db, cache
from config import UPLOADED_PHOTOS_DEST
import datetime
import re
import os


class Photo(db.Document):
	''' Stores basic meta-data for file uploaded to server.
	Photos are served using file_name field.'''
	file_name = db.StringField(required=True)
	file_type = db.StringField()
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	url = db.StringField()

	def __unicode__(self):

		return self.file_name

	def save(self, *args, **kwargs):
		if self.file_name:
			self.url = '/static/uploads' + self.file_name
			self.file_type = re.search(r'.*\.(.+)$', self.file_name, re.I).groups()[0]
		return super(Photo, self).save(*args, **kwargs)

	meta = {'indexes': [{'fields': ['$file_name', '$file_type'],
	                     'weights': {'file_name': 10, 'file_type': 2}
	                     }]}


class User_(db.Document):
	''' Basic user model document. Represented by combo of 
	first and last name.'''
	email = db.StringField(required=True)
	password = db.StringField(max_length=40)
	first_name = db.StringField(max_length=40)
	last_name = db.StringField(max_length=40)

	def __unicode__(self):

		return self.first_name + ' ' + self.last_name


class Category(db.Document):
	''' Category document referenced by Post. '''
	name = db.StringField(max_length=30)

	def __unicode__(self):

		return self.name


class Post(db.Document):
	''' Post document; see fields below. '''
	title = db.StringField(max_length=120, required=True)
	slug = db.StringField()
	created_at = db.DateTimeField(default=datetime.datetime.now, required=True)
	author = db.ReferenceField(User_)
	published = db.BooleanField(default=False)
	tags = db.ListField(db.StringField(max_length=30))
	index_background = db.ReferenceField(Photo)
	category = db.ReferenceField(Category)
	content = db.StringField(required=True)
	mark_delete = db.BooleanField(default=False)

	def save(self, *args, **kwargs):
		self.slug = re.sub('[^\w]+', '-', self.title.lower())
		return super(Post, self).save(*args, **kwargs)

	meta = {'indexes': [{'fields': ['$title', '$content'],
	                     'weights': {'title': 10, 'content': 2}
	                     }]}


def all_categories(posts):
	''' Takes PyMongoengine Posts document model, returns all categories
	for published posts. '''
	return {p.category for p in posts.objects(published=True)}


def all_tags(posts):
	''' Takes PyMongoengine Posts document model, returns all tags
	for published posts. '''
	return {tag for post in posts.objects(published=True) for tag in post.tags}
