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
        'Guitar',
        'Piano',
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
        {
            'name': 'Javascript',
            'img': './static/img/skills/js.png',
        },
        {
            'name': 'Typescript',
            'img': './static/img/skills/ts.png',
        },
        {
            'name': 'Angular',
            'img': './static/img/skills/angular.png',
        },
        {
            'name': 'Ionic',
            'img': './static/img/skills/ionic.png',
        },
        {
            'name': 'Python',
            'img': './static/img/skills/python.png',
        },
        {
            'name': 'React',
            'img': './static/img/skills/react.png',
        },
        {
            'name': 'SQL',
            'img': './static/img/skills/sql.png',
        },
        {
            'name': 'R',
            'img': './static/img/skills/r.png',
        },
        {
            'name': 'Flask',
            'img': './static/img/skills/flask.png',
        },
        ]
}

projects = [
    {
        'title': 'Flask Portfolio',
        'description': 'Created froms scratch a portfolio using Flask, SQL and Javascript. At the same time learned Github best practices using Issues and Pull Requests.',
        'date': 'June 2021',
        'img': './static/img/projects/web-dev.jpg',
        'url': 'www.github.com/LaloVene/porfolio-mlh',
    },
    {
        'title': 'Intelligent Room System',
        'description': 'Won first place in the Campus Engineering Expo by developing a mobile app which can be used to control a room´s light, fan, doors and windows in combination with a NodeMCU board. The app also connects to an API to get the current weather and use it to predict if it is going to rain using a Deep Learning model. I used Ionic, Firebase, Keras, ChartJS and TensorFlowJS.',
        'date': 'Dec 2020',
        'img': './static/img/projects/smart-house.jpg',
        'url': 'www.github.com/LaloVene/Intelligent-Room-Project',
    },
    {
        'title': 'Machine Learning Model For Financial Fraud Detection',
        'description': 'Got my Harvard’s Data Science certificate by making a ML model with R, where I predicted whether a bank transaction was fraud-ulent or not from a public dataset. I got a final accuracy of 0.99756 after cleaning the data and using a random forest ma-chine learning model.',
        'date': 'Aug 2020',
        'img': './static/img/projects/harvard.png',
        'url': 'www.github.com/LaloVene/Machine-Learning-Model-For-Financial-Fraud-Detection',
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
