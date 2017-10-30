from flask import Flask, request, redirect, render_template, session,url_for,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) # database object
app.secret_key = 'y337kGcys&zP3C'
title_error = ''
blog_error=''
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,blog,title,owner):
        self.blog = blog
        self.title = title
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self,username,password):
        self.username=username
        self.password=password

@app.before_request
def require_login():
    allowed_routes = ['login','signup','index','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        if request.endpoint == 'newpost':
           return redirect('login')
        elif request.endpoint == 'logout':
            return redirect('blog')
        else:     
            return redirect('/')
    
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('newpost')
        elif user and user.password != password:
            flash('User password incorrect','error')
            return render_template('login.html',username=username)
        elif not user:
            flash('User does not exist','error')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        min_length = 3
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #TODO -validate user's data
        if not username:
            flash('One or more fields are invalid','error')
            return redirect('signup')
        if not password:
            flash('One or more fields are invalid','error')
            return redirect('signup')
        if not verify:
            flash('One or more fields are invalid','error')
            return redirect('signup') 
        if len(username) < min_length:
            flash('username must be greater than 3 characters','error')
            return redirect('signup')
        if ' ' in username:
            flash('username cannot contain spaces')
            return redirect('signup')
        if len(password) < min_length:
            flash('password must be greater than 3 characters','error')
            return redirect('signup') 
        if password != verify:
            flash("passwords must match I can't stress this enough",'error')
            return redirect('signup')


        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('newpost')
        else:
            # TODO - user better response messaging
            flash('Username already exists sorry charlie','error')
            return redirect('signup')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    
    return redirect('blog')

@app.route('/')
def index():
    if request.method == 'POST':
        username = request.form['username']
    users = User.query.filter().all()
    return render_template('index.html',title="blog users!",users=users) #look at this line blogs=blogs
    
@app.route('/blog', methods=['POST','GET'])
def blog():
    blog = request.args.get('id')
    username = request.args.get('user')
    if blog:
        ind_blog = Blog.query.get(blog)
        return render_template('individual_blog.html',ind_blog=ind_blog)
    elif username:
        blog_user = User.query.filter_by(username=username).first()
        #print(blog_user)
        blogs = Blog.query.filter_by(owner=blog_user).all()
        return render_template('singleUser.html',blogs=blogs)
        
    else:
        blogs= Blog.query.all()


        return render_template('blog.html',blogs=blogs)

@app.route('/newpost', methods=['POST','GET'])
def newpost():

    user = User.query.get('id')
    if not user:
        redirect('login')
    blog = request.args.get('id')
    if blog:
        ind_blog = Blog.query.get(blog)
        return render_template('individual_blog.html',ind_blog=ind_blog)
  
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog = request.form['blog']
        title = request.form['title']
        if len(title)!=0 and len(blog) != 0:
            new_blog = Blog(blog,title,owner)
            db.session.add(new_blog)
            db.session.commit()
            new_direct = "/blog?id=" + str(new_blog.id)
            return redirect(new_direct)
        if len(title) == 0 and len(blog) ==0:
            blog_error = "Blog can't be left blank"
            title_error = "Title can't be left blank"
            return render_template("newpost.html",blog_error=blog_error,title_error=title_error)
        elif len(title)== 0 and len(blog) != 0:
            title_error = "Title can't be left blank"
            blog = request.form['blog']
            return render_template("newpost.html",blog=blog,title_error=title_error)
        elif len(blog) == 0 and len(title)!=0:
            blog_error = "Blog can't be left blank"
            title = request.form['title']
            return render_template('newpost.html',blog_error=blog_error,title=title)
    else:
        return render_template('newpost.html')
    
if __name__ == '__main__':
    app.run()