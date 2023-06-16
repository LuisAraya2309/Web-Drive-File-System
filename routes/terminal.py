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
    command_names = ["touch","mkdir","ls","cd","nano", "rm", "rmdir","mv","shr", "open", "pps", "load", "dl", "copy", "loadir", "dldir"]
    if command_type in command_names:
        
        #Touch command = Create new file in path given
        if command_type == "touch":
            file_created_successfully,message = file_system_db.create_file(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
            
            elif not file_created_successfully:
                error_alert = True
                alert_message = message
            
            else:
                success_alert = True
                success_message = "Archivo creado exitosamente"
            return render_template('main_page.html',**locals())

        elif command_type == "mkdir":
            dir_created_successfully, message = file_system_db.create_dir(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear más directorios."
                
            elif not dir_created_successfully:
                error_alert = True
                alert_message = message
            
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
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
            
            elif file_moved_successfully == 0:
                error_alert = True
                alert_message = "No se encontró ningún directorio o archivo con ese nombre."
            
            elif file_moved_successfully == 1 :
                success_alert = True
                success_message = "Se trasladó la información correctamente."
            
            else:
                error_alert = True
                alert_message = "Información inválida."
            return render_template('main_page.html',**locals())
        
        #Show file content
        elif command_type == "open":
            info = file_system_db.open_file(username, command_line, path)
            if not info:
                info = ""
                error_alert = True
                alert_message = "No existe un archivo con este nombre"
            return render_template('main_page.html',**locals())
        
        #Show file properties
        elif command_type == "pps":
            info = file_system_db.file_properties(username, command_line, path)
            if not info:
                info = ""
                error_alert = True
                alert_message = "No existe un archivo con este nombre"
            return render_template('main_page.html',**locals())
        
        #load file
        elif command_type == "load":
            copied_file = file_system_db.load_file(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
                
            elif not copied_file:
                error_alert = True
                alert_message = "Ya existe un archivo con este nombre o no se encontró el archivo"
            else:
                success_alert = True
                success_message = "Archivo copiado exitosamente"
            return render_template('main_page.html',**locals())
        
        #load dir
        elif command_type == "loadir":
            copied_file = file_system_db.load_dir(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
                
            elif not copied_file:
                error_alert = True
                alert_message = "Ya existe un directorio con este nombre o no se encontró el directorio"
            else:
                success_alert = True
                success_message = "Directorio copiado exitosamente"
            return render_template('main_page.html',**locals())
        
        #download file
        elif command_type == "dl":
            copied_file = file_system_db.download_file(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
                
            elif not copied_file:
                error_alert = True
                alert_message = "No existe un archivo con este nombre"
            else:
                success_alert = True
                success_message = "Archivo descargado exitosamente"
            return render_template('main_page.html',**locals())
        
        #download dir
        elif command_type == "dldir":
            copied_file = file_system_db.download_dir(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
                
            elif not copied_file:
                error_alert = True
                alert_message = "No existe un directorio con este nombre o ya fue descargado en esta ruta"
            else:
                success_alert = True
                success_message = "Directorio descargado exitosamente"
            return render_template('main_page.html',**locals())
        
        #copy file or dir
        elif command_type == "copy":
            file_moved_successfully = file_system_db.copy_file(username, command_line, path)
            
            if "shareData" in path:
                error_alert = True
                alert_message = "En esta caperta no puede crear archivos."
            
            elif file_moved_successfully == 0:
                error_alert = True
                alert_message = "No se encontró ningún directorio o archivo con ese nombre."
            
            elif file_moved_successfully == 1 :
                success_alert = True
                success_message = "Se copió la información correctamente."
            
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
            file_edited_successfully,message = file_system_db.edit_file(username, command_line, path)
            if not file_edited_successfully:
                error_alert = True
                alert_message = message
            else:
                success_alert = True
                success_message = "Archivo editado exitosamente"
            return render_template('main_page.html',**locals())
                 
    else:
        show_alert = True
        alert_message = "El comando ingresado no es válido"
        return render_template('main_page.html',**locals())    
    
