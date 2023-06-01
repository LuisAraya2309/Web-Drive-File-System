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
    
    def get_user_data(self,username : str):
        '''
        '''
        return ""

