from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from toolshare import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return AppUser.query.get(int(user_id))

class AppAdmin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column( db.String(64), nullable=False)
    last_name = db.Column( db.String(64), nullable=False)
    email_address = db.Column( db.String(128), unique=True, nullable=False)
    password = db.Column( db.String(64), nullable=False)

    def __repr__(self):
        return f"AppAdmin('{self.email_address}','{self.first_name}','{self.last_name}')"

class AppUser(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    yob = db.Column(db.Integer, nullable=False)
    email_address = db.Column(db.String(128), unique=True, nullable=False)
    post_code = db.Column(db.String(7), nullable=False)
    physical_address1 = db.Column(db.String(30))
    physical_address2 = db.Column(db.String(30))
    physical_address3 = db.Column(db.String(30))
    physical_address4 = db.Column(db.String(30))
    password = db.Column(db.String(64), nullable=False)
    id_img_reference = db.Column(db.String(32), unique=False)
    phone_number = db.Column(db.String(13), nullable=False)
    average_rating = db.Column(db.Float)
    pfp_img_reference = db.Column(db.String(32), nullable=False, default='default.jpg')
    subscribed = db.Column(db.Boolean(), nullable=False)

    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return AppUser.query.get(user_id)

    def __repr__(self):
        return f"AppUser('{self.email_address}','{self.first_name}','{self.last_name}', '{self.phone_number}','{self.average_rating}')"

class CardDetails(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), primary_key=True)
    holder_name = db.Column(db.String(30), nullable=False)
    account_no = db.Column(db.Integer, nullable=False)
    card_no = db.Column(db.Integer, nullable=False)
    sort_code = db.Column(db.Integer, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"CardDetails('{self.user_id}','{self.holder_name}')"


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), nullable=False)
    post_type = db.Column(db.String(20), nullable=False)
    post_title = db.Column(db.String(30), nullable=False)
    tool_type = db.Column(db.String(20), nullable=False)
    post_description = db.Column(db.String(250), nullable=False)
    post_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_reference = db.Column(db.String(64), nullable=False, default='tool.jpg')
    max_distance = db.Column(db.Integer)
    deposit = db.Column(db.Float, nullable=False)
    lending_duration = db.Column(db.Integer)
    post_code = db.Column(db.String(7), nullable=False)

    def __repr__(self):
        return f"Post('{self.post_title}','{self.post_type}', '{self.post_date}','{self.deposit}', '{self.post_description}')"


class Tools(db.Model):
    tool_id = db.Column(db.Integer, primary_key=True)
    tool_type = db.Column(db.String(70), nullable=False) 
    img_reference = db.Column(db.String(70), nullable=False, default='tool.jpg')

    def __repr__(self):
        return f"Tools('{self.tool_id}','{self.tool_type}')"

class Lending(db.Model):
    lending_reference = db.Column(db.Integer, primary_key=True)
    borrower_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade') ,nullable=False)
    lender_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade') ,nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id', ondelete='cascade') ,nullable=False)
    start_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"Lending('{self.lending_reference}','{self.start_date}','{self.borrower_id}','{self.lender_id}')"

class Messaging(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), primary_key=True)
    message_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, primary_key=True)
    message = db.Column(db.String(200))

    def __repr__(self):
        return f"Messaging('{self.user_id}','{self.message_time}','{self.message}')"


class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    report_title = db.Column(db.String(70), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id', ondelete='cascade'), nullable=False)

    def __repr__(self):
        return f"Report('{self.report_title}','{self.target_user_id}','{self.description}')"


class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey('app_user.id', ondelete='cascade'), nullable=False)
    review_text = db.Column(db.String(250))
    review_title = db.Column(db.String(70), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Review('{self.review_title}','{self.rating}','{self.target_user_id}')"
