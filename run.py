''' Runs our blog engine. Register blueprints, configurations and initialize
exetensions here. Clears cache before launching app.'''
from flask.ext.uploads import configure_uploads, patch_request_class
from blog import app, login_manager, md, admin, db, photos, cache
from blog.posts.models import Post
from blog.admin.posts import posts

app.config.from_object('config')
app.register_blueprint(posts)

# initialize extensions
configure_uploads(app, photos)
patch_request_class(app, 32 * 1024 * 1024)
login_manager.init_app(app)
md.init_app(app)
db.init_app(app)
cache.init_app(app, config=app.config)

with app.app_context():
	cache.clear()

if __name__ == '__main__':
	app.run(debug=True)
