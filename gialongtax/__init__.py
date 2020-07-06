import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)

secret_key = b'\xbb\xb0\x16x\x18n\x87\xa3#Q\x83\x9d\x91\xfe\xc7\x03'

app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt()


login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = ('Please log in to access this page.')

app.config['MAIL_SERVER'] = 'mailer-0104.inet.vn'
#app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'admin@gialongtax.com'
app.config['MAIL_PASSWORD'] = 'Gi@LongT@x123456'
#app.config['MAIL_USERNAME'] = '08play80@gmail.com'
#app.config['MAIL_PASSWORD'] = 'QWErty123456'
mail = Mail(app)

from gialongtax import routes