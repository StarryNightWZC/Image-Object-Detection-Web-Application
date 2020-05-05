from flask import request, redirect, url_for, render_template, flash
from flask_login import current_user
from passlib.handlers.sha2_crypt import sha256_crypt

from website.form import RegistrationForm
from website import app,db
from website.User import User
from website import utils
import json

@app.route('/register',methods=['GET','POST'])
def register():
    utils.record_requests(app.config['INSTANCE_ID'])
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    registerform=RegistrationForm(request.form)
    if request.method == 'POST' and registerform.validate():
        email=registerform.email.data
        username=registerform.username.data
        password=sha256_crypt.hash(str(registerform.password.data))
        #into db
        new_user=User(email=email,username=username,password=password)
        db.session.add(new_user)
        try:
            db.session.commit()
            print('-----already into database-----')
            flash('You are now registered successfully and can log in', 'success')
            return redirect(url_for('login'))
            #redirect(url_for('home'))
        except :
            db.session.rollback()
            print('-----rollback-----')
    return render_template('register.html',form=registerform)
@app.route('/api/register',methods=['POST','GET'])
def register_test():
    username=request.form.get('username')
    password=request.form.get('password')
    email=username+'@1779.com'
    hashpassword=sha256_crypt.hash(str(password))
    new_user=User(email=email,username=username,password=hashpassword)
    db.session.add(new_user)
    try:
        db.session.commit()
        return json.dumps({'Success':'You are now registered successfully and can log in'})
    except:
        db.session.rollback()
        return json.dumps({'Error':'Register Failed'})
