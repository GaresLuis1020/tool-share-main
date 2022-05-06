import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from toolshare import app, db, bcrypt, mail
from toolshare.forms import RegistrationForm, LoginForm, UpdateAccountForm, shortUpdateAccountForm, RequestResetForm, ResetPasswordForm, PostForm, SearchForm, RequestForm
from toolshare.models import AppAdmin, AppUser, CardDetails, Post, Tools, Lending, Messaging, Report, Review
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from werkzeug.urls import url_parse
import time


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.post_date.desc()).paginate(page=page, per_page=5)
    image_file = url_for('static', filename='tool_pictures/')
    return render_template('home.html', posts=posts, image_file=image_file)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/results", methods=('GET','POST'))
def results():
    page = request.args.get('page', 1, type=int)
    title = request.form['Search']
    if request.method=="POST":
        if not title:
            return redirect(url_for('home'))
        else:
            posts = Post.query.filter(Post.post_title.contains(title)).paginate(page=page, per_page=5)
            image_file = url_for('static', filename='tool_pictures/')
            return(render_template("results.html",posts=posts,title="Results",image_file=image_file))
        

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    picture_file = 'default.jpg'
    id_picture_file = ''
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
        if form.id_picture.data:
            id_picture_file = save_id_picture(form.id_picture.data)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = AppUser(first_name=form.forename.data, last_name = form.surname.data, email_address = form.email.data, password = hashed_password, yob = form.birthyear.data, post_code = form.postcode.data, phone_number = form.phone.data,
         physical_address1 = form.address1.data, physical_address2 = form.address2.data, physical_address3 = form.city.data, physical_address4=form.county.data, subscribed=form.mailing.data, pfp_img_reference = picture_file, id_img_reference = id_picture_file)
        db.session.add(user)
        db.session.commit()
        flash(f'Account has been created for {form.email.data}! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = AppUser.query.filter_by(email_address=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)    
        flash('Login Unsuccessful. Check the email and password!', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('Successfully Logged out!', 'success')
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(12)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pictures', picture_name)
    output_size = (150, 150)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name

def save_id_picture(form_picture):
    random_hex = secrets.token_hex(12)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/id_pictures', picture_name)
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name

def save_tool_picture(form_picture):
    random_hex = secrets.token_hex(12)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/tool_pictures', picture_name)
    output_size = (750, 750)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name


@app.route("/update_profile", methods=['GET', 'POST'])
@login_required
def account_update():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.pfp_img_reference = picture_file
        current_user.first_name = form.forename.data
        current_user.last_name = form.surname.data
        current_user.email_address = form.email.data
        current_user.post_code = form.postcode.data
        current_user.phone_number = form.phone.data
        current_user.physical_address1 = form.address1.data
        current_user.physical_address2 = form.address2.data
        current_user.physical_address3 = form.city.data
        current_user.physical_address4 = form.county.data
        current_user.subscribed = form.mailing.data
        db.session.commit()
        flash('Account has been updated!', 'success')
        return redirect(url_for('account_update'))
    elif request.method == 'GET':
        form.forename.data = current_user.first_name
        form.surname.data = current_user.last_name
        form.email.data = current_user.email_address
        form.postcode.data = current_user.post_code
        form.phone.data = current_user.phone_number
        form.address1.data = current_user.physical_address1
        form.address2.data = current_user.physical_address2
        form.city.data = current_user.physical_address3
        form.county.data = current_user.physical_address4
        form.mailing.data = current_user.subscribed
    image_file = url_for('static', filename='profile_pictures/' + current_user.pfp_img_reference)
    return render_template('update_profile.html', title='Account', image_file=image_file, form=form)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = shortUpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.forename.data
        current_user.last_name = form.surname.data
        current_user.email_address = form.email.data  
        db.session.commit()
        flash('Account has been updated!', 'success')
    elif request.method == 'GET':
        form.forename.data = current_user.first_name
        form.surname.data = current_user.last_name
        form.email.data = current_user.email_address
    image_file = url_for('static', filename='profile_pictures/' + current_user.pfp_img_reference)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='toolshare.recovery@gmail.com', recipients=[user.email_address])
    msg.body = f'''To reset your password, visit the following link: 
{url_for('reset_token', token=token, _external=True)}

If you did not make this request, then ignore this email and no changes will be made!
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = AppUser.query.filter_by(email_address=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with password reset instructions!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = AppUser.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password has been updated! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    picture_file = 'tool.jpg'
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_tool_picture(form.picture.data)
        post = Post(post_title=form.title.data, tool_type=form.tool_type.data, post_type=form.post_type.data, post_date=time.strftime('%Y-%m-%d %H:%M:%S'), image_reference=picture_file, max_distance=form.distance.data, deposit=form.deposit.data, lending_duration=form.duration.data, post_code=form.postcode.data, post_description=form.description.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your item post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('new_post.html', title='New Post', form=form, legend='Create a Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    image_file = url_for('static', filename='tool_pictures/')
    return render_template('post.html', title=post.post_title, post=post, image_file=image_file)

@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.post_type = form.post_type.data
        post.tool_type = form.tool_type.data
        post.post_title = form.title.data
        post.post_description = form.description.data
        post.deposit = form.deposit.data
        post.max_distance = form.distance.data
        post.lending_duration = form.duration.data
        post.post_code = form.postcode.data
        if form.picture.data:
            picture_file = save_tool_picture(form.picture.data)
            post.image_reference = picture_file
        db.session.commit()
        flash('Item information has been updated!', 'success')
        return redirect(url_for('post', post_id=post.post_id))
    elif request.method == 'GET':
        form.post_type.data = post.post_type
        form.tool_type.data = post.tool_type
        form.title.data = post.post_title
        form.description.data = post.post_description
        form.deposit.data = post.deposit
        form.distance.data = post.max_distance
        form.duration.data = post.lending_duration
        form.postcode.data = post.post_code
        form.picture.data = post.image_reference
    return render_template('new_post.html', title='Update Post', form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Item post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<int:id>")
def user_posts(id):
    page = request.args.get('page', 1, type=int)
    user = AppUser.query.filter_by(id=id).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.post_date.desc()).paginate(page=page, per_page=5)
    image_file = url_for('static', filename='tool_pictures/')
    return render_template('user_posts.html', posts=posts, image_file=image_file, user=user)


@app.route('/requestt',methods=['GET','POST'])
def requestt():
    form =RequestForm()

    return render_template('requestt.html',title='Request',form=form)

@app.route('/notification')
def notification():
 return render_template('notification.html',title='notification')
