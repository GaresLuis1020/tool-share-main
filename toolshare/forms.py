from decimal import ROUND_UP
from multiprocessing.sharedctypes import Value
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
import phonenumbers
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, ValidationError, NumberRange
from ukpostcodeutils import validation
from toolshare.models import AppUser


def validate_postcode(self, postcode):
        if not validation.is_valid_postcode(postcode.data):
            raise ValidationError('Invalid UK Post Code')

def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')

def validate_password(self, password):
    special_characters = '"!@#$%^&*()-+?_=,<>/"'
    userPassword = password.data
    string = "Password must contain at least "
    errors = []
    if not any(character in special_characters for character in userPassword):
        errors.append("one special character")
    if userPassword.islower() or userPassword.isdigit() :
        errors.append("one uppercase letter")
    if not any(character.isdigit() for character in userPassword):
        errors.append("one digit")
    if len(userPassword) < 10:
        errors.append("10 characters")  
    if errors:
        if len(errors) == 1:
            string = string + errors[0] + "."
            raise ValidationError(string)
        else: 
            for error in errors[:-1]:
                string = string + error + ", "
            string = string + "and " + errors[-1] + "."
        raise ValidationError(string)


class RegistrationForm(FlaskForm):
    forename = StringField('First Name', validators=[DataRequired(), Length(min=2, max=26)])
    surname =  StringField('Last Name', validators=[DataRequired(), Length(min=2, max=26)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    birthyear = IntegerField('Birth Year', validators=[DataRequired(), NumberRange(min=1900, max=2006)])
    postcode = StringField('Postcode', validators=[DataRequired(), validate_postcode])
    
    tos = BooleanField('Tick here to agree to Terms and Conditions and Privacy Policy (Required)', validators=[DataRequired()])
    mailing = BooleanField('Tick here to subscribe to our emailing services')

    phone = StringField('Phone', validators=[validate_phone])
    address1 = StringField('Address (Optional)', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    address2 = StringField('Address 2', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    county = StringField('County', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    city = StringField('City', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])

    picture = FileField('Add Profile Picture', validators=[FileAllowed(['jpg','png'])])
    id_picture = FileField('Add ID Picture', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = AppUser.query.filter_by(email_address=email.data).first()
        if user:
            raise ValidationError('This email is already taken! Please try another.')
    
    

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    forename = StringField('First Name', validators=[DataRequired(), Length(min=2, max=26)])
    surname =  StringField('Last Name', validators=[DataRequired(), Length(min=2, max=26)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    postcode = StringField('Postcode', validators=[DataRequired(), validate_postcode])

    mailing = BooleanField('Tick here to subscribe to our emailing Services')

    phone = StringField('Phone', validators=[validate_phone])
    address1 = StringField('Address (Optional)', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    address2 = StringField('Address 2', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    county = StringField('County', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])
    city = StringField('City', validators=[Length(min=2, max=30), Optional(strip_whitespace=True)])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])

    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email_address:
            email = AppUser.query.filter_by(email_address=email.data).first()
            if email:
                raise ValidationError('This email is already taken! Please try another.')

class shortUpdateAccountForm(FlaskForm):
    forename = StringField('First Name', validators=[DataRequired(), Length(min=2, max=26)], render_kw={"placeholder": "First Name"})
    surname =  StringField('Last Name', validators=[DataRequired(), Length(min=2, max=26)], render_kw={"placeholder": "Last Name"})
    email = StringField('Email Address', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email Address"})
    submit = SubmitField('Update Profile')

    def validate_email(self, email):
        if email.data != current_user.email_address:
            email = AppUser.query.filter_by(email_address=email.data).first()
            if email:
                raise ValidationError('This email is already taken! Please try another.')


class RequestResetForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        email = AppUser.query.filter_by(email_address=email.data).first()
        if email is None:
            raise ValidationError('The account with that email address does not exist!')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), validate_password])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class PostForm(FlaskForm):
    post_type = SelectField('Post Type', choices=['Borrowing', 'Lending'], validators=[DataRequired()])
    tool_type = SelectField('Post Type', choices=['Hammer', 'Screwdriver', 'Mallet', 'Axe', 'Saw', 'Scissors', 'Chisel', 'Pliers', 'Drill', 'Shovel', 'Other'], validators=[DataRequired()])
    title = StringField('Title', validators=[Length(min=2, max=30), DataRequired()])
    description = TextAreaField('Description', validators=[Length(min=2, max=250), DataRequired()])
    deposit = DecimalField('Deposit Amount', places=2, rounding=ROUND_UP, validators=[NumberRange(min=1, max=1000), DataRequired()])
    distance = IntegerField('Maximum Distance', validators=[DataRequired()])
    duration = IntegerField('Maximum Duration', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired(), validate_postcode])
    picture = FileField('Add Image', validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Post')

class SearchForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=2, max=30), DataRequired()])
    #post_type = SelectField('Post Type', choices=['Borrowing', 'Lending'], validators=[DataRequired()])  


class RequestForm(FlaskForm):
    message=StringField('Write your request details!',validators=[DataRequired(), Length(min=20, max=200)])
    submit=SubmitField('Send Request')

