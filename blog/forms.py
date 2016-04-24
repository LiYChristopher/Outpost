''' A set of basic forms for use in our blog engine. Powered by Flask-WTF
and Flask-MongoEngine. '''
import models
import posts
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from flask.ext.mongoengine.wtf import model_form


UserForm = model_form(models.User_)
PostForm = model_form(posts.models.Post, exclude=['created_at', 'slug'])
CategoryForm = model_form(posts.models.Category)


class LoginForm(Form):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	remember_me = BooleanField('remember_me', default=False)


class DeleteForm(Form):
	select_delete = BooleanField('', default=False)
	linked_post = StringField('slug', default=None)


class SearchForm(Form):
	query = StringField('query', validators=[DataRequired()])
