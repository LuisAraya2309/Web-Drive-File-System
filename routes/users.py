from flask import Blueprint, request, render_template
from db.file_system_db import file_system_db
users_mod = Blueprint('users', __name__)

#Globals
file_system_db = file_system_db()

# Login
@users_mod.route('/login',methods=["POST"])
def login():    
    username = request.form['username']
    password = request.form['password']
    logged = file_system_db.log_in(username=username,password=password)
    path = 'root/'
    return render_template('main_page.html',**locals()) if logged else "Not allowed"

# Sign Up
@users_mod.route('/sign_up',methods=["POST"])
def sign_up():    
    return render_template('sign_up.html')

# Register
@users_mod.route('/register',methods=["POST"])
def register():
    new_username = request.form['username']
    new_password = request.form['password']
    storage = request.form['storage']
    successful_register = file_system_db.register(username=new_username,password=new_password,storage=storage)
    if successful_register:
        return render_template('index.html', alert_message = True)
    else:
        return render_template('sign_up.html',alert_message = not successful_register)
