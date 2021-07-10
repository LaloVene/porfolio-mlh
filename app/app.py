import os
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
import json

import smtplib
from werkzeug.security import check_password_hash, generate_password_hash

# Database
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv()
app = Flask(__name__)

app.secret_key = "development key"

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{table}".format(
    user=os.getenv("POSTGRES_USER"),
    passwd=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=5432,
    table=os.getenv("POSTGRES_DB"),
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UserModel(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(), primary_key=True)
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<User {self.username}>"


class PostModel(db.Model):
    __tablename__ = "post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    like_count = db.Column(db.Integer, default=0)
    img = db.Column(db.Text, nullable=False)
    img_name = db.Column(db.Text, nullable=False)
    img_mimetype = db.Column(db.Text, nullable=False)


# Load JSON data
with open("page_data.json") as json_file:
    data = json.load(json_file)
    global headerInfo, aboutInfo
    headerInfo = data["headerInfo"]
    aboutInfo = data["aboutInfo"]
    projects = data["projects"]


# Pages
@app.route("/")
def index():
    return render_template(
        "about.html",
        title="MLH Fellow",
        url=os.getenv("URL"),
        headerInfo=headerInfo,
        aboutInfo=aboutInfo,
    )


@app.route("/about")
def aboutMe():
    return render_template("about.html", headerInfo=headerInfo, aboutInfo=aboutInfo)


@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html", headerInfo=headerInfo, projects=projects)


@app.route("/blog")
def blogPage():
    blog_posts = get_posts()
    path = "static/img/blog/"
    for post in blog_posts:
        post.content = post.content[:255] + "..."
        with open(path + post.img_name, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(post.img.encode("ascii"))
    return render_template(
        "blog.html", url=os.getenv("URL"), headerInfo=headerInfo, blog_posts=blog_posts
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", url=os.getenv("URL"), headerInfo=headerInfo)


@app.route("/sendMsg", methods=["POST"])
def sendMsg():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    if not name or not email or not message:
        return "Not enough data!", 400

    message2Send = "\nName: " + name + " \nEmail: " + email + "\nMessage: " + message
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("testmlh.pod.333@gmail.com", "iampod333")
    server.sendmail(
        "testmlh.pod.333@gmail.com", "testmlh.pod.333@gmail.com", message2Send
    )
    return render_template("success.html", url=os.getenv("URL"), headerInfo=headerInfo)


# Creating new blog posts
@app.route("/new-blog")
def new_blog():
    return render_template(
        "new_blog.html", title="New Blog", url=os.getenv("URL"), projects=projects
    )


@app.route("/upload", methods=["POST"])
def upload():
    pic = request.files["pic"]
    title = request.form["name"]
    content = request.form["blog-content"]

    if not pic or not title or not content:
        return "Not enough data!", 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return "Not enough data!", 400

    post = PostModel(
        title=title,
        content=content,
        img=pic.read(),
        img_name=filename,
        img_mimetype=mimetype,
    )
    db.session.add(post)
    db.session.commit()

    return render_template("success.html", url=os.getenv("URL"), headerInfo=headerInfo)


@app.route("/blog/<int:id>")
def get_post(id):
    post = PostModel.query.filter_by(id=id).first()
    if not post:
        return "Post Not Found!", 404

    return render_template(
        "detail_blog.html", url=os.getenv("URL"), title=post.title, post=post
    )


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif UserModel.query.filter_by(username=username).first() is not None:
            error = f"User {username} is already registered."

        if error is None:
            new_user = UserModel(username, generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            message = f"User {username} created successfully"
            return render_template(
                "login.html",
                url=os.getenv("URL"),
                headerInfo=headerInfo,
                message=message,
            )
        else:
            return (
                render_template(
                    "login.html",
                    url=os.getenv("URL"),
                    headerInfo=headerInfo,
                    message=error,
                ),
                418,
            )

    ## TODO: Return a restister page
    return render_template("register.html", url=os.getenv("URL"), headerInfo=headerInfo)


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        error = None
        user = UserModel.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            return redirect(url_for("portfolio"))
        else:
            return (
                render_template(
                    "login.html",
                    url=os.getenv("URL"),
                    headerInfo=headerInfo,
                    message=error,
                ),
                418,
            )

    ## TODO: Return a login page
    return render_template("login.html", url=os.getenv("URL"), headerInfo=headerInfo)


def get_posts():
    posts = PostModel.query.order_by(PostModel.date_created).all()
    return posts


# Health: For testing
@app.route("/health")
def check_health():
    return "Correct", 200
