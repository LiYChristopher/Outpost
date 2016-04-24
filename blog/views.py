''' Contains are client facing views. All views are
cached except for `detail`.'''
from blog import app, cache
from flask import request, render_template
from flask import redirect, url_for
from .posts.models import Post, Category
from .posts.models import all_tags, all_categories
from .forms import SearchForm


def make_cache_key(*args, **kwargs):
	''' Creates custom cache-key for views that require
	URL route parameters e.g. pages, search items. '''
	path = request.path
	if request.form.items():
		req_args = request.args.items() + request.form.values()
		args = str(hash(frozenset(req_args)))
	else:
		args = str(hash(frozenset(request.args.items())))
	return (path + args).encode('utf-8')


@app.route('/')
@app.route('/<int:page>', methods=['GET', 'POST'])
@cache.cached(key_prefix=make_cache_key)
def index(page=1):
	''' Route for index page.'''
	form = SearchForm(request.form)
	if request.method == "POST":
		q = form.query.data
		return redirect(url_for('search', query=q, page=1))
	published_only = Post.objects(published=True)
	posts = published_only.order_by('-created_at').paginate(page=page, per_page=6)
	return render_template('index.html', form=form,
										 posts=posts,
										 categories=all_categories(Post),
										 tags=all_tags(Post))


@app.route('/<slug>', methods=['GET', 'POST'])
def detail(slug):
	''' Route for actual article page.'''
	form = SearchForm(request.form)
	post = Post.objects(slug=slug, published=True)
	if not post:
		return redirect(url_for('unpublished'))
	post = post[0]
	return render_template('details.html', form=form,
		                                   slug=slug,
		                                   post=post)


@app.route("/--/", methods=['GET', 'POST'])
def unpublished():
	''' Dummy view for unpublished posts.'''
	return render_template('unpublished.html')


@app.route('/search/<query>/<int:page>', methods=['GET', 'POST'])
def search(query, page=1):
	''' Search function on blog views. '''
	if query is None:
		return redirect(url_for('index', page=1))
	form = SearchForm(request.form)
	posts = Post.objects.search_text(query).order_by("$text_score")
	posts = posts.paginate(page=page, per_page=6)
	return render_template('index.html',
							posts=posts,
							categories=all_categories(Post),
							tags=all_tags(Post),
							post_count=len(posts.items),
							form=form)


@app.route('/categories/<category_name>/<int:page>')
@cache.cached(key_prefix=make_cache_key)
def categories(category_name, page=1):
	''' Category view route. '''
	form = SearchForm(request.form)
	category = Category.objects(name=category_name)[0]
	posts = Post.objects(category=category).order_by('-created_at')
	posts = posts.paginate(page=page, per_page=6)
	cur_endpoint = request.endpoint
	if request.method == "POST":
		q = form.query.data
		return redirect(url_for('search', query=q, page=1))
	return render_template('index.html',
		                    cur_category=category_name,
							posts=posts,
							categories=all_categories(Post),
							tags=all_tags(Post),
							cur_endpoint=cur_endpoint,
							post_count=len(posts.items),
							form=form)


@app.route('/tags/<tag_name>/<int:page>')
@cache.cached(key_prefix=make_cache_key)
def tags(tag_name, page=1):
	''' Tag view route. '''
	form = SearchForm(request.form)
	posts = Post.objects(tags=tag_name).order_by('-created_at')
	posts = posts.paginate(page=page, per_page=6)
	if request.method == "POST":
		q = form.query.data
		return redirect(url_for('search', query=q, page=1))
	return render_template('index.html',
		                    cur_tag=tag_name,
							posts=posts,
							categories=all_categories(Post),
							tags=all_tags(Post),
							post_count=len(posts.items),
							form=form)
