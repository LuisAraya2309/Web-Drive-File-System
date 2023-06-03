from flask import Blueprint, request, render_template
from db.file_system_db import file_system_db
terminal_mod = Blueprint('terminal', __name__)

#Globals
file_system_db = file_system_db()

#Login
@terminal_mod.route('/process_command',methods=["POST"])
def process_command():
    command_line = request.form['command']
    command_entered = command_line.split(" ")
    command_type = command_entered[0] 
    username = request.form['username']
    path = request.form['path']
    command_names = ["touch","mkdir"]
    if command_type in command_names:
        
        #Touch command = Create new file in path given
        if command_type == "touch":
            file_created_successfully = file_system_db.create_file(username, command_line, path)
            if not file_created_successfully:
                error_alert = True
                alert_message = "Ya existe un archivo con ese nombre. Agregue --force para sobreescribir el archivo."
            else:
                success_alert = True
                success_message = "Archivo creado exitosamente"
            return render_template('main_page.html',**locals())

        elif command_type == "mkdir":
            dir_created_successfully = file_system_db.create_dir(username, command_line, path)
            if not dir_created_successfully:
                error_alert = True
                alert_message = "Ya existe un directorio con ese nombre. Agregue --force para sobreescribir el directorio."
            else:
                success_alert = True
                success_message = "Directorio creado exitosamente"    
            return render_template('main_page.html',**locals())
            
    else:
        show_alert = True
        alert_message = "El comando ingresado no es válido"
        return render_template('main_page.html',**locals())    
    
