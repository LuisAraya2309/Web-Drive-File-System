from flask import Blueprint, request, render_template
from db.db_connection import file_system_db
terminal_mod = Blueprint('terminal', __name__)

#Globals
file_system_db = file_system_db()

#Login
@terminal_mod.route('/process_command',methods=["POST"])
def process_command():    
    return render_template('main_page.html',**locals())
