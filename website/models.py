from . import db
from flask_login import UserMixin

tags = db.Table('user_tag',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

upvotes = db.Table('upvotes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    pfp = db.Column(db.String(150))
    about_me = db.Column(db.Text)
    description = db.Column(db.Text)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('users', lazy='dynamic'))
    friends = db.relationship('Friend',
                              foreign_keys='Friend.user_id',
                              backref='user',
                              lazy='dynamic')
    upvoted_posts = db.relationship('Post', secondary=upvotes, 
                                    backref=db.backref('upvoted_by', lazy='dynamic'))
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(100))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    content = db.Column(db.Text)
    upvotes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    media_file = db.Column(db.String)   
    date_of_creation = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_of_creation = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=[sender_id])
    body = db.Column(db.Text)
    date_of_creation = db.Column(db.DateTime)
