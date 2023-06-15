from datetime import datetime
import pymongo
import re


class file_system_db :
    def __init__(self) -> None:
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@filesystem-os.5ranjhw.mongodb.net")
        self.database = self.client["FileSystem-OS"]
        self.collection = self.database["Users_Data"]
        
    def get_all_data(self) -> list:
        collection_documents = [  document for document in self.collection.find() ]
        return collection_documents
    
    def get_user_data(self, username : str):
        find_user_pipeline = [ {'$match': {'user': username} } ]
        user_data = [ document for document in self.collection.aggregate(find_user_pipeline) ][0]
        return user_data
    
    def update_user_data(self,username : str, new_data : dict):
        self.collection.update_one({'user': username},{"$set":{"fileSystem":new_data}})
        
    def update_shared_data(self,username : str, new_data : dict):
        self.collection.update_one({'user': username},{"$set":{"sharedFiles":new_data}})
    
    def log_in(self,username : str, password : str):
        login_pipeline = [
                            {
                                '$match': {
                                    'user': username,
                                    'password': password
                                }
                            },
                            {
                                '$limit': 1
                            }
                        ]
        logged = self.collection.aggregate(login_pipeline).alive
        return logged
    
    def register(self, username : str, password : str, storage : int):
        user_exists_pipeline = [ {'$match': {'user': username} } ]
        user_exists = self.collection.aggregate(user_exists_pipeline).alive
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if user_exists:
            return False
        else:
            new_user_data = {
                                "user" : username,
                                "password" : password,
                                "storage" : storage,
                                "fileSystem" : { 
                                    "name" : "root",
                                    "creation_date" : timestamp,
                                    "modification_date" : timestamp,
                                    "childrenDirs" : [],
                                    "childrenDocs": []
                                },
                                "sharedFiles" : {
                                    "name" : "sharedFiles",
                                    "childrenDirs" : [],
                                    "childrenDocs" : []
                                }
                                
                            }
            #Register user
            self.collection.insert_one(new_user_data)
            return True
    
    def file_exists(self, username : str, file_name : str, path:str):
        # Example path: root/documents/
        dir_levels = path.split('/')[1:-1] # This deletes the empty character and root dir
        # dir_leves = ['documents']
        if "shareData" in path:
            user_data = self.get_user_data(username)['sharedFiles']
        else:    
            user_data = self.get_user_data(username)['fileSystem']
        
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs
                    break
        
        # Now we look for all the files in that level to see if the file exists
        dir_files = user_data['childrenDocs']
        for file in dir_files:
            if file['name'] == file_name:
                return True
        return False
    
    def dir_exists(self, username : str, dir_name : str, path:str):
        # Example path: root/documents/
        dir_levels = path.split('/')[1:-1] # This deletes the empty character and root dir
        # dir_leves = ['documents']
        if "shareData" in path:
            user_data = self.get_user_data(username)['sharedFiles']
        else:    
            user_data = self.get_user_data(username)['fileSystem']
        
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs
                    break
        
        # Now we look for all the children dirs in that level to see if the dir exists
        children_dirs = user_data['childrenDirs']
        for dir in children_dirs:
            if dir['name'] == dir_name:
                return True
        return False
        
    
    def create_file(self, username : str, command_line : str, path : str):
        file_name = command_line.split(' ')[1]
        file_content = re.findall(r'"(.*)"',command_line)[0]
        forced_touch = "--force" in command_line.replace(file_content,"")
        file_exists = self.file_exists(username,file_name,path)
        if file_exists and not forced_touch:
            return False,"Ya existe un archivo con ese nombre. Agregue --force para sobreescribir el archivo."
        
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        user_data = original_data['fileSystem']
        
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break
                
        dir_files = user_data['childrenDocs']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if file_exists: #Then we are going to override the file's content
            for file in dir_files:
                if file['name'] == file_name:
                    file['data'] = file_content
                    file['modification_date'] = timestamp        
                    break
                
        else: #Then we create the file
            dir_files.append({
                        "name" : file_name,
                        "creation_date" : timestamp,
                        "share_info" : [],
                        "modification_date" : timestamp,
                        "data" : file_content                        
                    })
        #Update user data
        if self.get_size_of_system(original_data) > int(original_data["storage"]):
            return False, "No hay espacio de almacenamiento suficiente"
        original_data = original_data['fileSystem']
        self.update_user_data(username, original_data)
        return True,""
    
    def create_dir(self, username : str, command_line : str, path : str):
        dir_name = command_line.split(' ')[1]
        forced_mkdir = '--force' in command_line
        dir_exists = self.dir_exists(username, dir_name, path)
        if dir_exists and not forced_mkdir:
            return False,"Ya existe un directorio con ese nombre. Agregue --force para sobreescribir el directorio."
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        user_data = original_data['fileSystem']
        
        #First we navigate to actual path
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break           
        children_dirs = user_data['childrenDirs']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if dir_exists: #Then we are going to override the dir
            for dirs in children_dirs:
                if dirs['name'] == dir_name:
                    dirs['childrenDirs'] = []
                    dirs['childrenDocs'] = []
                    dirs['modification_date'] = timestamp
                    break
        else: #Then we create the directory
            children_dirs.append({
                "name" : dir_name,
                "creation_date" : timestamp,
                "modification_date" : timestamp,
                "childrenDirs" : [],
                "childrenDocs" : []
            })
            
        #Update user data
        if self.get_size_of_system(original_data) > int(original_data["storage"]):
            return False, "No hay espacio de almacenamiento suficiente"
        original_data = original_data['fileSystem']
        self.update_user_data(username, original_data)
        return True,""
    
    def delete_dir(self, username : str, command_line : str, path : str):
        
        dir_name = command_line.split(' ')[1]
        dir_exists = self.dir_exists(username, dir_name, path)
        if not dir_exists:
            return False
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        
        #First we navigate to actual path
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break           
        
        children_dirs = user_data['childrenDirs']
        #Then we create the directory
        for dirs in range(len(children_dirs)):
            if children_dirs[dirs]["name"] == dir_name:
                del children_dirs[dirs]
                break
                
        #Update user data
        if "shareData" in path:
            original_data = original_data['sharedFiles']
            self.update_shared_data(username, original_data)
        else:
            original_data = original_data['fileSystem']
            self.update_user_data(username, original_data)
        return True
    
    def delete_file(self, username : str, command_line : str, path : str):
        
        file_name = command_line.split(' ')[1]
        file_exists = self.file_exists(username,file_name,path)
        if not file_exists:
            return False
        
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break
                
        dir_files = user_data['childrenDocs']
            
        for index, file in enumerate(dir_files):
            if file["name"] == file_name:
                del dir_files[index]
                break
                
        #Update user data
        if "shareData" in path:
            original_data = original_data['sharedFiles']
            self.update_shared_data(username, original_data)
        else:
            original_data = original_data['fileSystem']
            self.update_user_data(username, original_data)
        return True
    
    def move_file(self, username : str, command_line : str, path : str):
        
        try:
            file_name, destination_path = command_line.split(' ')[1:]
            file_exists = self.file_exists(username,file_name,path)
            dir_exists = self.dir_exists(username,file_name,path)

            dir_levels = path.split('/')[1:-1]
            new_dir_levels = destination_path.split('/')[1:-1]
            original_data = self.get_user_data(username)
            
            user_data = original_data['fileSystem']
            for level in dir_levels:
                for dirs in user_data['childrenDirs']:
                    if dirs['name'] == level:
                        user_data = dirs           
                        break
            
            new_dir_files = original_data['fileSystem']
            for level in new_dir_levels:
                for dirs in new_dir_files['childrenDirs']:
                    if dirs['name'] == level:
                        new_dir_files = dirs           
                        break
                        
            if new_dir_files == original_data['fileSystem'] and destination_path != "root/":
                return 2
            
            if file_exists:
                dir_files = user_data['childrenDocs']
                for index, file in enumerate(dir_files):
                    if file["name"] == file_name:
                        new_dir_files['childrenDocs'].append(file)
                        del dir_files[index]
                        break
                
            elif dir_exists:
                children_dirs = user_data['childrenDirs']
                for index, dirs in enumerate(children_dirs):
                    if dirs["name"] == file_name:
                        new_dir_files['childrenDirs'].append(dirs)
                        del children_dirs[index]
                        break
                    
            original_data = original_data['fileSystem']
            self.update_user_data(username, original_data)
            return 1
        
        except :
            return 2
        
        
    def already_shared(self, file: list, username: str):
        for user in file:
            if user == username:
                return False
        return True
    
    def move_through_data(self, shared_dir: dict, new_user: str, file_name: str):
        for file in shared_dir['childrenDocs']:
            if file['name'] == file_name:
                #update shared_info
                file['share_info'].append(new_user)
                return True   
            
        for directory in shared_dir['childrenDirs']:
            # Go to next set of files
            print(directory['name'])
            self.move_through_data(directory, new_user, file_name)
       
    def update_shared_user(self,users: list, file_name: str, new_user: str):
        
        for index, user in enumerate(users):
            print(user)
            all_user_data = self.get_user_data(user)
            if index == 0:
                print("Entre a cambiar al primero")
                user_data = all_user_data['fileSystem']
                self.move_through_data(user_data, new_user, file_name)
                all_user_data = all_user_data['fileSystem']
                self.update_user_data(user, all_user_data)   
            else:
                user_data = all_user_data['sharedFiles']
                self.move_through_data(user_data, new_user, file_name)
                all_user_data = all_user_data['sharedFiles']
                self.update_shared_data(user, all_user_data) 
    
    def update_shared_info(self, shared_dir: dict, new_user: str, username: str):
        
        for file in shared_dir['childrenDocs']:
            if self.already_shared(file["share_info"], new_user):
                self.update_shared_user(file['share_info'], file['name'], new_user)
                #update shared_info
                if len(file["share_info"]) == 0:
                    file['share_info'].append(username)
                
                file['share_info'].append(new_user)
            
        for directory in shared_dir['childrenDirs']:
            # Go to next set of files
            self.update_shared_info(directory, new_user, username)
    
    def share_info(self, username : str, command_line : str, path : str):
        user_name, file_name = command_line.split(' ')[1:]
        file_exists = self.file_exists(username,file_name,path)
        dir_exists = self.dir_exists(username,file_name,path)
        
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        new_original_data = self.get_user_data(user_name)
        
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        new_user_data = new_original_data['sharedFiles']
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs
                    break
        
        if file_exists:
            dir_files = user_data['childrenDocs']
            for file in dir_files:
                if file["name"] == file_name:
                    if self.already_shared(file["share_info"], user_name):
                        
                        new_user_data['childrenDocs'].append(file)
                        self.update_shared_user(file["share_info"], file["name"], user_name)
                        if len(file["share_info"]) == 0:
                            new_user_data['childrenDocs'][-1]["share_info"] += [username]
                            
                        file["share_info"].append(user_name)
                        break
        
        elif dir_exists:
            children_dirs = user_data['childrenDirs']
            for index, dirs in enumerate(children_dirs):
                if dirs["name"] == file_name:
                
                    shared_dir = children_dirs[index]
                    #Change every file share_info attribute
                    self.update_shared_info(shared_dir,user_name, username)
                    
                    new_user_data['childrenDirs'].append(shared_dir)
                    break
        else:
            return False    
                
        if "shareData" in path:
            original_data = original_data['sharedFiles']
            self.update_shared_data(username, original_data)
        else:
            original_data = original_data['fileSystem']
            self.update_user_data(username, original_data)
        
        new_original_data = new_original_data['sharedFiles']
        self.update_shared_data(user_name, new_original_data)
    
        return True
    
    
    def list_dir(self, username : str, path : str):
        result = ""
        dir_levels = path.split('/')[:-1] # This deletes the empty character 

        if "shareData" in dir_levels:
            user_data = self.get_user_data(username)['sharedFiles']
        else:
            user_data = self.get_user_data(username)['fileSystem']

        print("dir levels",dir_levels)
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    
                    user_data = dirs
                    break
        for direc in user_data["childrenDirs"]:
            result += direc["name"]+"/\n"
        for doc in user_data["childrenDocs"]:
            result += doc["name"]+"\n"
        
        return result
    
    def enter_dir(self, username : str, path : str, command_line : str):
        new_dir = command_line.split(' ')[1]
        if new_dir == "..":
            
            return True,'/'.join(path.split('/')[:-2])+'/'
        
        dir_levels = path.split('/')[:-1] # This deletes the empty character 
        
        if new_dir== "shareData" or "shareData" in dir_levels:
            user_data = self.get_user_data(username)['sharedFiles']
            print(dir_levels)
            if "shareData" in dir_levels:
                for level in dir_levels:
                    for dirs in user_data['childrenDirs']:
                        if dirs['name'] == level:
                            user_data = dirs
                            break
                for direc in user_data["childrenDirs"]:
                    if new_dir == direc["name"]:
                        return True,path +new_dir+"/"
            else:
                return True,path +new_dir+"/"
            
        user_data = self.get_user_data(username)['fileSystem']
        
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs
                    break
        for direc in user_data["childrenDirs"]:
            if new_dir == direc["name"]:
                print("Existe")
                return True,path +new_dir+"/"
          
        
        print("NO EXISTE")
        return False,"Este directorio no existe en "+path
    
    def move_update_message(self, shared_dir: dict, new_message: str, file_name: str, timestamp: str):
        for file in shared_dir['childrenDocs']:
            if file['name'] == file_name:
                #update shared_info
                file['data'] = new_message
                file['modification_date'] = timestamp
                return True 
            
        for directory in shared_dir['childrenDirs']:
            # Go to next set of files
            self.move_update_message(directory, new_message, file_name, timestamp)
    
    def update_message(self, users: list, file_name: str, new_message: str, timestamp: str):
        for index, user in enumerate(users):
            all_user_data = self.get_user_data(user)
            
            if index == 0:
                user_data = all_user_data['fileSystem']
                self.move_update_message(user_data, new_message, file_name, timestamp)
                all_user_data = all_user_data['fileSystem']
                self.update_user_data(user, all_user_data)   
            else:
                user_data = all_user_data['sharedFiles']
                self.move_update_message(user_data, new_message, file_name, timestamp)
                all_user_data = all_user_data['sharedFiles']
                self.update_shared_data(user, all_user_data)   
       
    
    def edit_file(self, username : str, command_line : str, path : str):
        file_name = command_line.split(' ')[1]
        file_content = re.findall(r'"(.*)"',command_line)[0]
        
        file_exists = self.file_exists(username,file_name,path)
        
        if not file_exists:
            return False,""
        
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break
                
        dir_files = user_data['childrenDocs']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for file in dir_files:
            if file['name'] == file_name:
                file['data'] = file_content
                file['modification_date'] = timestamp
                self.update_message(file['share_info'], file['name'], file_content, timestamp)
                break
                
        #Update user data
        
        if "shareData" in path:
            original_data = original_data['sharedFiles']
            self.update_shared_data(username, original_data)
        else:
            if self.get_size_of_system(original_data) > int(original_data["storage"]):
                return False, "No hay espacio de almacenamiento suficiente"
            original_data = original_data['fileSystem']
            self.update_user_data(username, original_data)
        
        return True,""
    

    #Open file
    def open_file(self, username : str, command_line : str, path : str):
        file_name = command_line.split(' ')[1]

        file_exists = self.file_exists(username,file_name,path)
        
        if not file_exists:
            return False
        
        info = ""
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break
        
        dir_files = user_data['childrenDocs']
        for file in dir_files:
            if file['name'] == file_name:
                info = file['data']       
                break
        
        return info
    
    #File properties
    def file_properties(self, username : str, command_line : str, path : str):
        file_name = command_line.split(' ')[1]

        file_exists = self.file_exists(username,file_name,path)
        
        if not file_exists:
            return False
        
        properties = ""
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        if "shareData" in path:
            user_data = original_data['sharedFiles']
        else:
            user_data = original_data['fileSystem']
        #First we locate the directory
        for level in dir_levels:
            for dirs in user_data['childrenDirs']:
                if dirs['name'] == level:
                    user_data = dirs           
                    break
        
        dir_files = user_data['childrenDocs']
        for file in dir_files:
            if file['name'] == file_name:
                properties += "Nombre y extensión: "+file['name']+"\n"
                properties += "Fecha de creación: "+file['creation_date']+"\n"
                properties += "Fecha de modificación: "+file['modification_date']+"\n"
                properties += "Tamaño: "
                break
        
        return properties
    
    #Copy file from real to virtual (load)
    def load_file(self, username : str, command_line : str, path : str):
        file_path = command_line.split(' ')[1]
        file_name = file_path.split('/')[-1:][0]

        if self.file_exists(username, file_name, path):
            return False

        file = open(file_path, 'r')
        file_lines = file.readlines()
        file_content = ""

        for line in file_lines:
            file_content += line
        
        file.close()

        return self.create_file(username, "touch "+file_name+" \""+file_content+"\"", path)
    
    def get_size_of_system(self, file_system:dict):
        root = file_system["fileSystem"]
        sharedFiles = file_system["sharedFiles"]
        bytes_size = 0
        bytes_size += self.get_size_of_system_aux(root) + self.get_size_of_system_aux(sharedFiles)
        return bytes_size
        
        
    def get_size_of_system_aux(self, file_system:dict):
        bytes_size = len(file_system["name"])+len(file_system["creation_date"])+len(file_system["modification_date"])
        
        for docs in file_system["childrenDocs"]:
            bytes_size += len(docs["data"])+ len(docs["name"])+len(docs["creation_date"])+len(docs["modification_date"])
            
            
        for dirs in file_system["childrenDirs"]:
            bytes_size += self.get_size_of_system_aux(dirs)
        return bytes_size

        