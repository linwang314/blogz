from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'CuPR9LcX7GzRWvQT'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref = 'owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/")
def index():
    users = User.query.all()
    return render_template('/index.html', users=users)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            flash('Username does NOT exist', 'error')
        elif user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Incorrect password', 'error')
            
    return render_template('login.html', title="Login")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        
        if (username is None) or (password is None) or (verify is None):
            flash('One or more invalid fields')
        elif existing_user:
            flash('Username already exists')
        elif len(username) < 3 or len(username) > 20:
            flash('Invalid username')
        elif len(password) < 3 or len(password) > 20:
            flash('Invalid password')
        elif password != verify:
            flash("Passwords don't match")
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html', title="Signup")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/blog")
def blog():
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')
        
    if blog_id is not None:
        blog = Blog.query.get(blog_id)
        return render_template('page.html', blog=blog)
    if blog_user is not None:
        user_id = User.query.filter_by(username=blog_user).first().id
        blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('posts.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs)

@app.route("/newpost", methods=['GET','POST'])
def newpost():

    blog_owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        
        if blog_title == '':
            flash('No blog title')
        if blog_body == '':
            flash('Not blog content')

        if blog_title and blog_body:
            new_blog = Blog(blog_title, blog_body, blog_owner)
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