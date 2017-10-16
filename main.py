from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog3:blogging@localhost:8889/build-a-blog3'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app) # database object
title_error = ''
blog_error=''
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(300))


    def __init__(self,blog,title):
        self.blog = blog
        self.title = title


@app.route('/blog', methods=['POST','GET'])
def blog():
    
    if request.method == 'POST':
        blog = request.form['blog']
        title = request.form['title']
        if len(title) == 0 and len(blog) ==0:
            blog_error = "Blog can't be left blank"
            title_error = "Title can't be left blank"
            return render_template('newpost.html',blog_error=blog_error,title_error=title_error)
        elif len(title)== 0:
            title_error = "Title can't be left blank"
            return render_template('newpost.html',title_error=title_error)
        elif len(blog) == 0:
            blog_error = "Blog can't be left blank"
            return render_template('newpost.html',blog_error=blog_error)
        else:
            new_blog = Blog(blog,title)
            db.session.add(new_blog)
            db.session.commit()

    blogs= Blog.query.all()
    titles = Blog.query.all()
    
    return render_template('blog.html',blogs=blogs,titles=titles)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    
    return render_template('newpost.html',**locals())

if __name__ == '__main__':
    app.run()