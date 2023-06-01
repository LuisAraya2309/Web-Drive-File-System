from flask import Blueprint, request, render_template
from db.db_connection import file_system_db
users_mod = Blueprint('users', __name__)

#Globals
file_system_db = file_system_db()

# Login
@users_mod.route('/login',methods=["POST"])
def login():    
    username = request.form['username']
    password = request.form['password']
    logged = file_system_db.log_in(username=username,password=password)
    path = '/'
    return render_template('main_page.html',**locals()) if logged else "Not allowed"

# Register
@users_mod.route('/sign_up',methods=["POST"])
def register():    
    return render_template('sign_up.html')
