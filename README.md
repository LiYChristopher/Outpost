## Flask Blog Engine
This is a simple blog engine, cobbled together using Flask and various extensions with a MongoDB backend. It includes
a basic front-end view of posts, filterable by either category or tag, as well as text search.

Content is managed through an admin dashboard that allows you to create, edit or delete post(s). 
You can also perform similar operations for Categories and Images to be used in posts.
An excellent JavaScript text editor is provided by Summernote. Content in the Posts and Image Gallery
views are sortable by various database fields.

For those who are newer to Flask, this might be useful to see how Blueprints work, how various
extensions fit into the overall application, and how a MongoDB driven Flask App looks like in general.

Similar code happens to power my own hosted blog.

## Extensions Used

- Flask-Login
- Flask-Misaka
- Flask-Cache
- Flask-Upload
- Flask-Mongoengine
- Flask-WTF

