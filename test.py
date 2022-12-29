from pymongo import MongoClient
from pymongo import errors as MongoErrors
from pymongo.database import Database as MongoDatabase
from jasmin_mongo_configuration.interceptorsinstaller import InterceptorsInstaller
import inspect
# mongoclient = MongoClient('mongodb://d71Rkc8Y6:wL5UPFLOHGhrb@mongodb1:27017,mongodb2:27017,mongodb3:27017/?authSource=admin&replicaSet=rs')
# database: MongoDatabase = mongoclient['admin']
# print(database.command({'getClusterParameter': "changeStreamOptions"}))

# preAndPostImagesExpireAfterSeconds = clusterParameter[
#     'clusterParameters'][0]['preAndPostImages']['expireAfterSeconds']
             
rr = InterceptorsInstaller(host='127.0.0.1')
print('****************************************')
print(inspect.getsource(rr.mo))
print('****************************************')