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
        if user_exists:
            return False
        else:
            new_user_data = {
                                "user" : username,
                                "password" : password,
                                "storage" : storage,
                                "fileSystem" : { 
                                    "name" : "root",
                                    "childrenDirs" : [],
                                    "childrenDocs": []
                                },
                                "sharedFiles" : {
                                    "name" : "sharedFiles",
                                    "childrenDocs" : []
                                }
                                
                            }
            #Register user
            self.collection.insert(new_user_data)
            return True
    
    def file_exists(self, username : str, file_name : str, path:str):
        # Example path: root/documents/
        dir_levels = path.split('/')[1:-1] # This deletes the empty character and root dir
        # dir_leves = ['documents']
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
    
    def create_file(self, username : str, command_line : str, path : str):
        file_name = command_line.split(' ')[1]
        file_content = re.findall(r'"(.*)"',command_line)[0]
        forced_touch = "--force" in command_line.replace(file_content,"")
        file_exists = self.file_exists(username,file_name,path)
        if file_exists and not forced_touch:
            return False
        
        dir_levels = path.split('/')[1:-1]
        original_data = self.get_user_data(username)
        print('INICIO', original_data)
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
        self.update_user_data(username, user_data)
        return True
