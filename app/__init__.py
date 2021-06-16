import os
from flask import Flask, request, Response, render_template, send_file, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from db import db_init, db
from models import Blog
import smtplib

load_dotenv()
app = Flask(__name__)
 
app.secret_key = 'development key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db_init(app)

headerInfo = {
    'img':'./static/img/coverimg.jpg',
    'name': 'Eduardo Venegas',
    'intro': 'CS Student'
}

aboutInfo = {
    'shortParagraph': 'Hi! My name is Eduardo Venegas. I am a 3rd year CS student, full time Web Developer and Data Engineer. I love learning new things and playing piano / guitar.',
    'education': [
        {
            'schoolName': 'Bachelor in CS - ITESM',
            'year': '2019 - Present',
            'desc': '60 % Tuition scholarship due to academic merit.\n• GPA: 97.27\n• Won first place in the Campus Engineering Expo.\n• Achieved one of the best GPA 3 times.\n• Member of the Algorithm Club school group.',
        },
        {
            'schoolName': 'Technologist High School in Automatic Control and Instrumentation - CETI',
            'year': '2015 - 2019',
            'desc': 'Thesis Project: Autonomous Tennis Machine.\n• GPA: 93',
        }
    ],
    'interest': [
        'Learning',
        'Dancing',
        'Running',
        ],
    'experience': [
        {
            'jobTitle': 'Production Engineering Fellow - MLH Fellowship powered by Facebook and GitHub',
            'year': 'Jun 2021 - Aug 2021 • 3 mos',
            'jobDesc': 'Working as Production Engineer, it´s hybrid between software & systems engineering that works across product & infrastructure to make sure services are reliable & scalable.'
        },
        {
            'year': ' Jun 2021 • 9 mos',
            'jobTitle': 'Full Stack Engineer - Data Engineer',
            'year': 'Mar 2021 – Jun 2021 • 4 mos',
            'jobDesc': 'Use mathematical and statistical technics over data in order to get the most important features and create ML models that generate predictions as well as valuable insights. Then incorporate these models and analysis in an endpoint for easy access. Using technologies such as Python and Flask.'
        },
        {
            'jobTitle': 'Full Stack Engineer - Jiit Technolohies',
            'year': 'Oct 2020 – Jun 2021 • 9 mos',
            'jobDesc': 'Developing a platform for COVID tracking, a Marketplace site and a platform that can organize its inventory, human resources, shipments, income and expenses, that uses AI/ML. Using technologies such as Angular, Ionic, Typescript, Cordova, SQL and Flask.'
        },
    ],
    'skill': [
        'Javascript / Typescript',
        'Angular',
        'Ionic',
        'Python',
        'React',
        'SQL',
        'R',
        'Flask',
        'Data Science',
        ]
}

projects = [
    {
        'title': 'Flask Web App',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.',
        'date': '06/09/2021',
        'img': './static/img/projects/web-dev.jpg',
        'url': 'www.github.com',
    },
    {
        'title': 'Machine Learning Project For Data Prediction',
        'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. In eu sapien and lorem fermentum hendrerit quis mattis arcu. Nulla eget efficitur ex. Proin hendrerit ligula quis vehicula interdum.',
        'date': '06/09/2021',
        'img': './static/img/projects/machine-learning.jpg',
        'url': 'www.github.com',
    },
]


# Pages
@app.route('/')
def index():
    return render_template('about.html', title="MLH Fellow", url=os.getenv("URL"), headerInfo=headerInfo, aboutInfo=aboutInfo)

@app.route('/about')
def aboutMe():
    return render_template('about.html', headerInfo=headerInfo, aboutInfo=aboutInfo)


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html', headerInfo=headerInfo, projects=projects)


@app.route('/blog')
def blogPage():
    blog_posts = get_posts()
    path = 'app/static/img/blog/'
    for post in blog_posts:
        post.content = post.content[:255] + '...'
        with open(path + post.img_name, "wb") as binary_file:
            # Write bytes to file
            binary_file.write(post.img)
    return render_template('blog.html', url=os.getenv("URL"), headerInfo=headerInfo, blog_posts=blog_posts)

@app.route('/contact')
def contact():
    return render_template('contact.html', url=os.getenv("URL"), headerInfo=headerInfo)


@app.route('/sendMsg', methods=['POST'])
def sendMsg():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    if not name or not email or not message:
        return 'Not enough data!', 400

    message2Send = '\nName: ' + name + ' \nEmail: ' + email + '\nMessage: ' + message
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('testmlh.pod.333@gmail.com', 'iampod333')
    server.sendmail('testmlh.pod.333@gmail.com', 'testmlh.pod.333@gmail.com', message2Send)
    return render_template('success.html', url=os.getenv("URL"), headerInfo=headerInfo)


# Creating new blog posts
@app.route('/new-blog')
def new_blog():
    return render_template('new_blog.html', title="New Blog", url=os.getenv("URL"), projects=projects)


@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    title = request.form['name']
    content = request.form['blog-content']

    if not pic or not title or not content:
        return 'Not enough data!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Not enough data!', 400

    post = Blog(title=title, content=content, img=pic.read(), img_name=filename, img_mimetype=mimetype)
    db.session.add(post)
    db.session.commit()

    return render_template('success.html', url=os.getenv("URL"), headerInfo=headerInfo)


@app.route('/blog/<int:id>')
def get_post(id):
    post = Blog.query.filter_by(id=id).first()
    if not post:
        return 'Post Not Found!', 404

    return render_template('detail_blog.html', url=os.getenv("URL"), title=post.title, post=post)


def get_posts():
    posts = Blog.query.order_by(Blog.date_created).all()
    return posts
