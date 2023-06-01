#Mongo driver import
import pymongo

class file_system_db :
    def __init__(self) -> None:
        self.client = pymongo.MongoClient("mongodb+srv://admin:admin@filesystem-os.5ranjhw.mongodb.net")
        self.database = self.client["FileSystem-OS"]
        self.collection = self.database["Users_Data"]
        
    def get_all_data(self) -> list:
        collection_documents = [  document for document in self.collection.find() ]
        return collection_documents
    
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

