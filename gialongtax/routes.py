import os
from os.path import join, dirname, realpath
import requests, json, pymsgbox
from werkzeug.utils import secure_filename
from flask import render_template, session, redirect, url_for, request, flash, abort, Blueprint
from gialongtax import app, db, bcrypt, mail
from gialongtax.forms import LoginForm, ContactForm, PostForm, RegistrationForm
from gialongtax.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

# sys.path.insert(0, os.path.dirname(__file__))

imgpaths = os.path.join('static', 'imgs')
UPLOADS_PATH = join(dirname(realpath(__file__)), 'static\imgs')
secret_key = b'\xbb\xb0\x16x\x18n\x87\xa3#Q\x83\x9d\x91\xfe\xc7\x03'
google_site_key = '6LeK3aQZAAAAABz5oAZJGQsE-TenuZxmMPBGoMjH'
google_secret_key = '6LeK3aQZAAAAADxJHISZLtg1AISIg78dJnsOWk4_'

app.config['SECRET_KEY'] = secret_key
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = google_site_key
app.config['RECAPTCHA_PRIVATE_KEY'] = google_secret_key
app.config['UPLOAD_FOLDER'] = UPLOADS_PATH
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def start(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python v' + sys.version.split()[0] + '\n'
    response = '\n'.join([message, version])
    return [response.encode()]

@app.route("/")
@app.route('/index')
def index():
    dataform = request.form
    formlogs = LoginForm(dataform)
    formregs = RegistrationForm(dataform)
    formconts = ContactForm(dataform)
    formpost = PostForm(dataform)
    post_news = Post.query.filter_by(posttyle=1).all()
    post_services = Post.query.filter_by(posttyle=2).all()
    post_customers = Post.query.filter_by(posttyle=3).all()
    return render_template('index.html',current_user=current_user, imgpath=imgpaths, sitekey=google_site_key, 
                            formpost=formpost, formlogs=formlogs, formconts=formconts, formregs=formregs, 
                            post_news=post_news, post_services=post_services, post_customers=post_customers)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == "POST":
        dataform = request.form
        formlogs = LoginForm(dataform)
        captcha_response = dataform.get('g-recaptcha-response')
        if is_human(captcha_response, google_secret_key):
            if formlogs.validate_on_submit():
                #hash_password = bcrypt.generate_password_hash(formlogs.password.data).decode('utf-8')
                user = User.query.filter_by(email=formlogs.email.data).first()
                if user and bcrypt.check_password_hash(user.password_hash, formlogs.password.data):
                    login_user(user)
                else:
                    pymsgbox.alert("Wrong username or password!","Log In")
            else:
                pymsgbox.alert(formlogs.errors,"Log In")
        else:
            pymsgbox.alert("Please confirm you are not a robot","Log In")
    return redirect('/')

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == "POST":
        dataform = request.form
        formconts = ContactForm(dataform) 
        captcha_response = dataform.get('g-recaptcha-response')    
        if is_human(captcha_response, google_secret_key):
            if formconts.validate_on_submit():
                msg = Message(formconts.subject.data, sender=formconts.email.data, recipients=['admin@gialongtax.com'])
                msg.body = 'Kính gửi Cty Gia Long\r\n\r\n' +  formconts.content.data + '\r\n\r\nTrân trọng cảm ơn\r\n' + formconts.username.data
                mail.send(msg)
                pymsgbox.alert('Send success!',"Send Us")
            else:
                pymsgbox.alert(formconts.errors,"Send Us")
        else:
            pymsgbox.alert('Please confirm you are not a robot.',"Send Us")
    return redirect('/')

@app.route('/newspost', methods=['POST'])
@login_required
def newspost():
    if current_user.is_authenticated:
        dataform = request.form
        fpost = PostForm(dataform)
        if request.method == "POST":
            captcha_response = dataform.get('g-recaptcha-response')
            if is_human(captcha_response, google_secret_key):
                if fpost.validate_on_submit():
                    # check if the post request has the file part
                    if 'imagefile' not in request.files:
                        pymsgbox.alert("No file part","danger")
                        return redirect(request.url)
                    file = request.files['imagefile']
                    # if user does not select file, browser also submit an empty part without filename
                    if file.filename == '':
                        pymsgbox.alert("No selected file","danger")
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        #file.save(os.path.join(UPLOADS_PATH,filename))
                        file.save(os.path.join(app.root_path, 'static/imgs', filename))
                    #Put data into database
                    post = Post(posttyle=fpost.posttyle.data,title=fpost.title.data,content=fpost.content.data,image_file=filename,author=current_user)
                    db.session.add(post)
                    db.session.commit()
                    pymsgbox.alert("Post success!","info")
                else:
                    pymsgbox.alert(fpost.errors,"News Post")
            else:
                pymsgbox.alert('Please confirm you are not a robot.',"warning")         
    else:
        return render_template('404.html')
    return redirect('/')

def is_human(captcha_response,secret):   
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['POST'])
@login_required
def register():
    if current_user.is_authenticated:
        dataform = request.form
        formreg = RegistrationForm(dataform)
        if current_user.isAdmin:
            if formreg.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(formreg.password.data).decode('utf-8')
                user = User(fullname=formreg.fullname.data, email=formreg.email.data, password_hash=hashed_password)
                db.session.add(user)
                db.session.commit()
                pymsgbox.alert("New user has been created","Info")
            else:
                pymsgbox.alert(formreg.errors,"Log In")
        else:
            pymsgbox.alert("You are not Gia Long Administrator","Alert")
    else:
        return render_template('404.html')
    return redirect('/')
    
@app.route("/updatepost/<int:post_id>", methods=['POST'])
@login_required
def updatepost(post_id):
    getpost = Post.query.get_or_404(post_id)
    if getpost.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        file = request.files['imagefile']
        if file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.root_path, 'static/imgs', filename))
        getpost.title = form.title.data
        getpost.content = form.content.data
        db.session.commit()
        pymsgbox.alert('Your post has been updated!', 'success')
    else:
        pymsgbox.alert(form.errors,"Update Post")
    return redirect(url_for('index'))

@app.route("/delete_post/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    pymsgbox.alert('Your post has been deleted!', 'success')
    return redirect(url_for('/'))
