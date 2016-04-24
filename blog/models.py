''' Contains a simple MongoDB document schema for our User class. '''
from blog import db


class User_(db.Document):
	email = db.StringField(required=True)
	password = db.StringField(max_length=40)
	first_name = db.StringField(max_length=40)
	last_name = db.StringField(max_length=40)

	def __unicode__(self):

		return self.first_name + ' ' + self.last_name
