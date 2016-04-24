''' This file includes all the admin views for our basic blog engine.
Views are prefixed with '/admin', enforced by a blueprint called `posts`.
Views are protected with Flask-Login.
'''
from flask import Blueprint, render_template, flash, request
from flask import request, redirect, url_for, send_from_directory
from flask.ext.login import UserMixin, login_required
from flask.ext.login import login_user, logout_user
from flask.ext.uploads import UploadNotAllowed
from blog import app, login_manager, photos, cache
from blog.posts.models import Post, Category, Photo, User_
from blog.forms import DeleteForm, PostForm
from blog.forms import LoginForm, CategoryForm, SearchForm
from mongoengine.errors import ValidationError
import re
import os


posts = Blueprint('posts', __name__, url_prefix='/admin')


class User(UserMixin):

	users = {}

	def __init__(self, email, password):
		self.id = unicode(email)
		self.password = password
		mongo_user = User_.objects(email=email, password=password)[0]
		self.name = mongo_user.__str__()
		self.users[self.id] = self

	@classmethod
	def get(cls, user_id):
		if cls.users:
			if user_id in cls.users:
				return cls.users[user_id]
		else:
			return None


@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)


@posts.route('/', methods=['GET', 'POST'])
@login_required
def admin():
	''' Index page for Admin dashboard.'''
	return render_template('/admin/index.html')


@posts.route('/login', methods=['GET', 'POST'])
def login():
	''' Wraps flask-login's login method. '''
	form = LoginForm(request.form)
	if request.method == 'POST':
		if not form.validate():
			flash('Invalid login information. Please try again.')
		else:
			email, password = request.form['email'], request.form['password']
			if not User_.objects(email=email, password=password):
				flash("Incorrect credentials. Please try again.")
			else:
				admin = User(form.email.data, form.password.data)
				login_user(admin)
				return redirect(url_for('posts.admin'))
	return render_template('login.html', form=form)


@posts.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	'''Wraps flask-login's logout_user method.'''
	logout_user()
	flash("You have logged out!")
	return redirect(url_for('posts.login'))


@app.errorhandler(401)
def not_authorized_401(e):
	return render_template('/admin/401.html', e=e)


@app.errorhandler(404)
def not_authorized_404(e):
	return render_template('/admin/404.html', e=e)


def make_cache_key(*args, **kwargs):
	''' Creates custom cache-key for views that require
	URL route parameters e.g. pages, search items. '''
	path = request.path
	args = str(hash(frozenset(request.args.items())))
	return (path + args).encode('utf-8')


def process_tags(tag_string):
	''' inputs: String of tags, values separated by commas
		outputs: List of tags, to be saved to a post document
	'''
	tags = re.findall(r'[A-Za-z0-9_-]{2,}', tag_string.lower(), re.I)
	return tags


def existing_slug(slug):
	''' Checks if slug exists in dB. If so, create an
	alternative slug. Else return none.'''
	iter_num = 1
	alt_slug = None
	existing_records = Post.objects(slug=slug)
	while existing_records:
		alt_slug = slug + str(iter_num)
		existing_records = Post.objects(slug=alt_slug)
		iter_num += 1
	if alt_slug:
		return alt_slug
	return None


@posts.route('/upload/<redirect_endpoint>', methods=['POST'])
def upload(**kwargs):
	''' Handles writing of file from upload form to disk.
	will redirect to previous URL.'''
	url_args = {}
	if request.args:
		url_args = {arg: request.args[arg] for arg in request.args}
	# HTML formatting error - check that redirect URLS are correct
	try:
		redirect_endpoint = kwargs.get('redirect_endpoint')
		if redirect_endpoint:
			del kwargs['redirect_endpoint']
	except Exception as e:
		flash('An error has occured - please contact admin.')
		return redirect(url_for(redirect_endpoint, **url_args))
	# If POST, process file. If filetype forbidden, flash error
	if request.method == 'POST':
		if request.files.get('index_background'):
			try:
				file_name = photos.save(request.files['index_background'])
				post_background_image = Photo(file_name=file_name)
				post_background_image.save()
				flash("Image '{}' has been saved!".format(file_name))
			except UploadNotAllowed:
				flash('This file type is not allowed.')
	return redirect(url_for(redirect_endpoint, **url_args))


@posts.route('/all_posts/search/<query>/<int:page>', methods=['GET', 'POST'])
def post_search(query, page=1):
	''' MongoDB text search for admin panel on Post model.'''
	form = SearchForm(request.form)
	posts = Post.objects.search_text(query).order_by('$text_score')
	posts = posts.paginate(page=page, per_page=6)
	return render_template('admin/list.html',
							posts=posts,
							form=form,
							cur_endpoint='posts.all_posts')


@posts.route('/all_posts/')
@posts.route('/all_posts/<sort>/<int:page>', methods=['GET', 'POST'])
@login_required
def all_posts(page=1, sort='-created_at'):
	''' List of posts in admin view that are published, paginated and sortable.'''
	form = SearchForm(request.form)
	posts = Post.objects.order_by(sort).paginate(page, per_page=6)
	delete = PostForm()
	if request.method == 'POST':
		if 'multidelete' in request.form:
			slugs = [form for form in request.form if form != 'multidelete']
			mark_for_deletion(slugs)
			return redirect(url_for('posts.delete_selected'))
		elif request.form.get('query'):
			q = form.query.data
			return redirect(url_for('posts.post_search', query=q, page=1))
	return render_template("/admin/list.html",
						   posts=posts, 
						   delete=delete,
						   form=form,
						   cur_endpoint=request.endpoint)


def mark_for_deletion(slugs):
	''' Helper function for delete_selected route. Sets
	mark_delete field to True for all posts.'''
	# Unmark for deletion all previous posts
	all_posts = Post.objects()
	for p in all_posts:
		p.mark_delete = False
		p.save()
	for slug in slugs:
		if not Post.objects(slug=slug):
			continue
		post = Post.objects.get_or_404(slug=slug)
		post.mark_delete = True
		post.save()
	return


@posts.route('/published/')
@posts.route('/published/<sort>/<int:page>', methods=['GET', 'POST'])
@login_required
def published(page=1, sort='-created_at'):
	''' List of posts in admin view that are published, paginated and sortable.'''
	form = SearchForm(request.form)
	posts = Post.objects(published=True).order_by(sort).paginate(page, per_page=6)
	if request.method == 'POST' and form.validate_on_submit():
		redirect(url_for('posts.published', page=page))
	return render_template("/admin/list.html",
		                   posts=posts,
		                   form=form,
		                   cur_endpoint=request.endpoint)


@posts.route('/drafts/')
@posts.route('/drafts/<sort>/<int:page>', methods=['GET', 'POST'])
@login_required
def drafts(page=1, sort='-created_at'):
	''' Lists of posts in admin view that are not published, paginated and sortable.'''
	form = SearchForm(request.form)
	posts = Post.objects(published=False).order_by(sort).paginate(page, per_page=6)
	if request.method == 'POST' and form.validate_on_submit():
		redirect(url_for('posts.drafts', page=page))
	return render_template("/admin/list.html",
		                   posts=posts,
		                   form=form,
		                   cur_endpoint=request.endpoint)


@posts.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
	''' Create new post from admin view. '''
	form = PostForm(request.form)
	if request.method == 'POST' and form.validate_on_submit():
		post_args = {}
		if Post.objects(title=form.title.data):
			flash("Post with this title already exists!")
			return render_template('/admin/new_post.html', form=form)
		if request.form.get('new_tags'):
			post_args['tags'] = process_tags(request.form.get('new_tags'))
		post_args['index_background'] = form.index_background.data
		post_args['published'] = form.published.data
		post_args['title'] = form.title.data
		post_args['author'] = form.author.data
		post_args['content'] = form.content.data
		post_args['category'] = form.category.data
		new_post = Post(**post_args)
		new_post.save()
		flash("New post, '{}', successfully created!".format(new_post.title))
		return redirect(url_for('posts.edit_post', slug=new_post.slug))
	return render_template('/admin/new_post.html', form=form)


@posts.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
	''' Post edit view of admin panel '''
	post = Post.objects(slug=slug)[0]
	form = PostForm(request.form, obj=post)
	if request.method == 'POST' and form.validate_on_submit():
		post.title = request.form.get('title')
		post.author = form.author.data
		if request.form.get('new_tags'):
			new_tags = process_tags(request.form['new_tags'])
			post.tags = new_tags
		post.index_background = form.index_background.data
		post.category = form.category.data
		post.published = form.published.data
		post.content = request.form.get('content')
		post.save()
		flash('Post has been edited')
		return redirect(url_for('posts.edit_post', slug=post.slug))

	return render_template("/admin/edit_post.html", form=form, slug=slug)


@posts.route('/delete/<slug>', methods=['GET', 'POST'])
@login_required
def delete_post(slug):
	''' Delete single or multiple posts on admin panel. '''
	post = Post.objects(slug=slug)[0]
	if request.method == 'POST':
		Post.delete(post)
		flash("Post has been deleted.")
		return redirect(url_for('posts.all_posts', sort='-created_at', page=1))
	return render_template('/admin/delete_post.html', post=post, slug=slug)


@posts.route('/delete/all_selected', methods=['GET', 'POST'])
@login_required
def delete_selected():
	to_delete = Post.objects(mark_delete=True)
	if not to_delete:
		flash('Nein')
		return redirect(url_for('posts.all_posts', sort='-created_at', page=1))
	if request.method == 'POST':
		for post in to_delete:
			Post.delete(post)
			post.save()
		flash("{} Posts have been deleted.".format(len(to_delete)))
		return redirect(url_for('posts.all_posts', sort='-created_at', page=1))
	return render_template('/admin/delete_post.html', to_delete=to_delete)


@posts.route('/categories/')
@posts.route('/categories/<int:page>', methods=['GET', 'POST'])
@login_required
def categories(page=1):
	''' Admin view for categories; create and
	delete functionality included.'''
	form = CategoryForm(request.form)
	categories = Category.objects.paginate(page=page, per_page=10)
	if request.method == 'POST' and form.validate_on_submit():
		if Category.objects(name=form.name.data):
			flash('Category already exists')
			return redirect(url_for('posts.categories', page=1))
		new_category = Category(form.name.data)
		new_category.save()
		return redirect(url_for('posts.categories', page=1))
	return render_template('/admin/categories.html', post=Post, form=form, categories=categories)


@posts.route('/categories/delete/<name>', methods=['GET', 'POST'])
@login_required
def delete_category(name):
	''' Delete specified category, redirects to admin/categories. '''
	category = Category.objects(name=name)[0]
	posts = Post.objects
	if request.method == 'POST':
		Category.delete(category)
		flash("Category '{}' has been deleted.".format(name))
		remove_category(posts)
	return redirect(url_for('posts.categories', page=1))


def remove_category(posts):
	''' If post's category no longer in dB, remove it from the post. '''
	if not Category.objects(name='None'):
		none = Category(name='None')
		none.save()
	none = Category.objects(name='None')[0]
	for post in posts:
		if not getattr(post.category, 'name', 0):
			post.update(category=none)
		elif not Category.objects(name=post.category.name):
			post.update(category=none)
	return


@posts.route('/image_gallery/all/<sort>/<int:page>', methods=['GET', 'POST'])
@login_required
def image_gallery(page=1, sort='-created_at'):
	''' Manage images within admin panel.'''
	form = SearchForm(request.form)
	if request.method == 'POST':
		q = form.query.data
		return redirect(url_for('posts.image_search', query=q, page=1))
	images = Photo.objects.order_by(sort).paginate(page=page, per_page=6)
	return render_template('/admin/image_gallery.html', images=images, form=form)


@posts.route('/image_gallery/search/<query>/<int:page>', methods=['GET', 'POST'])
@login_required
def image_search(query, page=1):
	''' Search for images within gallery in admin panel.'''
	form = SearchForm(request.form)
	images = Photo.objects.search_text(query).order_by('$file_name')
	images = images.paginate(page=page, per_page=6)
	return render_template('/admin/image_gallery.html', images=images, form=form)


@posts.route('/image_gallery/<file_name>')
@login_required
def image_item(file_name):
	''' Serves image within admin panel.'''
	return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], file_name)


@posts.route('/image_gallery/delete/<file_name>', methods=['POST'])
@login_required
def delete_image_item(file_name, **kwargs):
	''' Deletes specified image meta-data/file from dB
	and storage folder, respectively.'''
	url_args = {}
	if request.args:
		url_args = {arg: request.args[arg] for arg in request.args}
	image = Photo.objects(file_name=file_name)[0]
	if request.method == 'POST':
		Photo.delete(image)
		os.remove(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_name))
		image.save()
		flash("Image '{}' has been deleted.".format(file_name))
	return redirect(url_for('posts.image_gallery', **url_args))
