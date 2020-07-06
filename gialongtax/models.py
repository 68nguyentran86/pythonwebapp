from datetime import datetime
from gialongtax import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.Text(100))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    isAdmin = db.Column(db.Boolean(), nullable=False, default=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        #return '<User {}>'.format(self.email)
        return f"User('{self.fullname}', '{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posttyle = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text(250), nullable=False)
    date_posted = db.Column(db.DateTime, index=True, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text(), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        #return '<Post {}>'.format(self.contents)
        return f"Post('{self.posttyle}','{self.title}','{self.date_posted}','{self.content}','{self.image_file}')"
