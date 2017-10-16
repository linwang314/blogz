from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog")
def blog():
    blog_id = request.args.get('id')
    if blog_id is not None:
        blog_title = Blog.query.get(blog_id).title
        blog_body = Blog.query.get(blog_id).body
        return render_template('page.html', blog_title=blog_title, blog_body=blog_body)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs)

@app.route("/newpost", methods=['GET','POST'])
def newpost():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''

        if blog_title == '':
            title_error = 'Please add the title of the blog.'
        if blog_body == '':
            body_error = 'Please add the content of the blog.'

        if not title_error and not body_error:
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = Blog.query.order_by("id desc").first().id
            return redirect("/blog?id={0}".format(new_blog_id))
        else:
            return render_template('newpost.html', title="Add a Blog Entry",
                title_error=title_error, body_error=body_error)

    return render_template('newpost.html', title="Add a Blog Entry")

if __name__ == '__main__':
    app.run()