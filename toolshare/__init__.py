import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
#Set these secret keys into an environment variables
app.config['SECRET_KEY'] = '2ca7bf2068898f558a7f4118ee00d71f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c2045720:*SH0vELSbRUSHEs&SaWs@csmysql.cs.cf.ac.uk:3306/c2045720_toolshare'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')
mail = Mail(app)

from toolshare import routes