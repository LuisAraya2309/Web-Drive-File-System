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
    command_names = ["touch","mkdir","ls","cd","nano", "rm", "rmdir","mv","shr"]
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
        
        elif command_type == "ls":
            info = file_system_db.list_dir(username, path)
            return render_template('main_page.html',**locals())
        
        elif command_type == "cd":
            succesful_enter,new_path = file_system_db.enter_dir(username, path, command_line)
            if succesful_enter:
                path = new_path
                return render_template('main_page.html',**locals())
            error_alert = succesful_enter
            alert_message = new_path
            return render_template('main_page.html',**locals())
        
        elif command_type == "rm":
            file_deleted_successfully = file_system_db.delete_file(username, command_line, path)
            if not file_deleted_successfully:
                error_alert = True
                alert_message = "No se encontró ningún archivo con ese nombre."
            else:
                success_alert = True
                success_message = "Archivo eliminado exitosamente."
            return render_template('main_page.html',**locals())
        
        elif command_type == "rmdir":
            dir_deleted_successfully = file_system_db.delete_dir(username, command_line, path)
            if not dir_deleted_successfully:
                error_alert = True
                alert_message = "No se encontró ningún directorio con ese nombre."
            else:
                success_alert = True
                success_message = "Directorio eliminado exitosamente."
            return render_template('main_page.html',**locals())
        
        elif command_type == "mv":
            file_moved_successfully = file_system_db.move_file(username, command_line, path)
            if file_moved_successfully == 0:
                error_alert = True
                alert_message = "No se encontró ningún directorio o archivo con ese nombre."
            elif file_moved_successfully == 1 :
                success_alert = True
                success_message = "Se traslado la información correctamente."
            else:
                error_alert = True
                alert_message = "Información inválida."
            return render_template('main_page.html',**locals())
        
        elif command_type == "shr":
            info_shr_successfully = file_system_db.share_info(username, command_line, path)
            if not info_shr_successfully:
                error_alert = True
                alert_message = "No se encontró ningún directorio o archivo con ese nombre."
            else:
                success_alert = True
                success_message = "Información compartida exitosamente."
            return render_template('main_page.html',**locals())
        
        if command_type == "nano":
            file_edited_successfully = file_system_db.edit_file(username, command_line, path)
            if not file_edited_successfully:
                error_alert = True
                alert_message = "No existe un archivo con este nombre para poder editar"
            else:
                success_alert = True
                success_message = "Archivo editado exitosamente"
            return render_template('main_page.html',**locals())
            
    else:
        show_alert = True
        alert_message = "El comando ingresado no es válido"
        return render_template('main_page.html',**locals())    
    
