from datetime import datetime
from functools import wraps

from website import app, login_manager, db
from flask import render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user

from passlib.hash import sha256_crypt
from functools import wraps
import os

from werkzeug.utils import secure_filename

from website.Photo import Photo
from website.User import User
from website.form import LoginForm
from website.objectdetection import object_detection
import boto3
import traceback
from website import utils

import json
import botocore

import s3transfer


APP_ROOT=os.path.dirname(os.path.abspath(__file__))

@app.route('/')
@app.route('/home')
def home():
    utils.record_requests(app.config['INSTANCE_ID'])
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login',methods=['GET','POST'])
def login():
    utils.record_requests(app.config['INSTANCE_ID'])
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit:
        #Get formfield
        user_object=User.query.filter_by(username=form.username.data).first()
        print(form.username.data)
        print(user_object)
        if form.username.data is not None:
            if user_object is not None:
                if (sha256_crypt.verify(form.password.data, user_object.password)):
                    login_user(user_object)
                    # If a page accessible only to logged in users is accessed before logging in
                    next_page = request.args.get('next')
                    flash('You have logged in','success')
                    return redirect(next_page) if next_page else redirect(url_for('dashboard'))
                else:
                    flash("Your password is worng, please try again", 'danger')
            else:
                flash("Account does not exists", 'danger')
    return render_template('login.html',form=form)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_authenticated:
            print(current_user)
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
@is_logged_in
def logout():
    utils.record_requests(app.config['INSTANCE_ID'])
    logout_user()
    flash('You are now loggout out','success')
    return redirect(url_for('login'))


#Dashboard
@app.route('/dashboard',methods=['GET','POST'])
@is_logged_in
def dashboard():
    utils.record_requests(app.config['INSTANCE_ID'])
    # Let's use Amazon S3
    s3 = boto3.client('s3')

    target = os.path.join(APP_ROOT,'images')
    targetoutput=os.path.join(APP_ROOT,'output/')
    if not os.path.isdir(target):
        os.mkdir(target)

    if not os.path.isdir(targetoutput):
        os.mkdir(targetoutput)

    #需要添加：空文件检测+文件上传限制
    for file in request.files.getlist("file"):
        if request.files['file'].filename == '':
            flash('You need to choose a file', 'danger')
            return redirect(url_for('dashboard'))
        #print(file)
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        #use timestamp to prevent when same image is uploaded twice
        path=str(timestamp)+'_'+file.filename
        destination="/".join([target,path])
        destinationoutput="/".join([targetoutput,path])
        file.save(destination)
        #Upload picture to S3
        s3.upload_file(destination, app.config['BUCKET_NAME'], current_user.get_id()+'/user_images/{}'.format(path))
        object_detection(destination,destinationoutput,path)
        #to db
        new_photo=Photo(username=current_user.get_username(),photourl=path)
        db.session.add(new_photo)
        try:
            db.session.commit()
            print('-----already into database-----')
            flash('Upload photos successfully! Go to gallery to check the result.', 'success')
            os.remove(destinationoutput)
            os.remove(destination)
        except:
            db.session.rollback()
            print('-----rollback-----')

    return render_template('dashboard.html')

@app.route('/dashboard/<filename>')
def send_image_original(filename):
    utils.record_requests(app.config['INSTANCE_ID'])
    return send_from_directory("images", filename)

@app.route('/gallery/<filename>')
def send_image_detect_result(filename):
    utils.record_requests(app.config['INSTANCE_ID'])
    return send_from_directory("output", filename)

#Add Photos
@app.route('/gallery')
@is_logged_in
def get_gallery():
    utils.record_requests(app.config['INSTANCE_ID'])
    photos=[]
    s3 = boto3.client('s3')
    photos_object=Photo.query.filter_by(username=current_user.get_username()).all()
    for photo in photos_object:
        photos.append(photo.photourl)
        s3.download_file(app.config['BUCKET_NAME'], current_user.get_id() + '/user_images/' +photo.photourl,
                         'website/images/'+photo.photourl)
        s3.download_file(app.config['BUCKET_NAME'], current_user.get_id() + '/user_images_results/' + photo.photourl,
                         'website/output/' + photo.photourl)
    return render_template("gallery.html",image_names=photos)

@app.route('/showimg/<filename>')
def showimg(filename):
    return render_template('showimg.html',outputname=filename)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/api/upload',methods=['POST'])
def uploadtest():

    utils.record_requests(app.config['INSTANCE_ID'])
    s3 = boto3.client('s3')

    target = os.path.join(APP_ROOT, 'images/')
    targetoutput = os.path.join(APP_ROOT, 'output/')
    if not os.path.isdir(target):
        os.mkdir(target)

    if not os.path.isdir(targetoutput):
        os.mkdir(targetoutput)
    try:
        if request.method != 'POST':
            return 'invalid request method'

        # check user
        valid = True
        username = request.values['username']
        password = request.values['password']

        user = User.query.filter_by(username=username).first()

        if user:
            if not (sha256_crypt.verify(password, user.password)):
                valid = False
                message = "Username or Password does not exist"
        else:
            valid = False
            message = "Username or Password does not exist"

        if valid:
            login_user(user)
            if 'file' in request.files:
                file = request.files['file']
                filename = secure_filename(file.filename)
                if filename != '':
                    if not file:
                        message = 'file is empty'
                    elif not allowed_file(filename):
                        print(filename)
                        message = 'invalid file type'
                    else:
                        # updload file
                        now = datetime.now()
                        timestamp = datetime.timestamp(now)
                        # use timestamp to prevent when same image is uploaded twice
                        path = str(timestamp) + '_' + file.filename
                        print(path)
                        destination = "/".join([target, path])
                        destinationoutput = "/".join([targetoutput, path])
                        file.save(destination)
                        # Upload picture to S3
                        s3.upload_file(destination, app.config['BUCKET_NAME'],
                                       current_user.get_id() + '/user_images/{}'.format(path))
                        print(destination)
                        object_detection(destination, destinationoutput, path)
                        # to db
                        new_photo = Photo(username=current_user.get_username(), photourl=path)
                        db.session.add(new_photo)
                        try:
                            db.session.commit()
                            os.remove(destinationoutput)
                            os.remove(destination)
                            message = file.filename + ' upload success'
                        except:
                            db.session.rollback()
                            message = file.filename + ' upload fail'
                else:
                    message = 'no selected file'
            else:
                message = 'no name [file] in form data'

        return message
    except Exception as e:
        print(e)
        traceback.print_tb(e.__traceback__)
        return 'Upload Fail'

