"""
Jasmin MongoDB Configuration - MT Interceptor

This interceptor is used to check if a user have enough credit to send a message

Requirements:
    - pymongo: pip install pymongo
"""
import os

from pymongo import MongoClient
from pymongo import errors as MongoErrors
from pymongo.collection import Collection as MongoCollection
from pymongo.database import Database as MongoDatabase

# Get MongoDB connection parameters
MONGO_CONNECTION_STRING = os.getenv(
    'MONGO_CONNECTION_STRING', 'mongodb://{$MONGODB_USERNAME}:{$MONGODB_PASSWORD}@mongodb1:27017,mongodb2:27017,mongodb3:27017/?authSource=admin&replicaSet=rs')
MONGO_BILLING_DATABASE = os.getenv(
    'MONGO_BILLING_DATABASE', 'configs')
MONGO_BILLING_COLLECTION = os.getenv(
    'MONGO_BILLING_COLLECTION', 'user')
MONGO_BILLING_FIELD = os.getenv(
    'MONGO_BILLING_FIELD', 'mt_messaging_cred quota sms_count')


def charge_MT(user_id, amount):
    """Charge a user for a message

    :param user_id: The user id
    :type user_id: str
    :param amount: The amount to charge
    :type amount: int
    :return: The SMPP status
    :rtype: int
    """
    try:
        mongoclient = MongoClient(MONGO_CONNECTION_STRING)
        server_info = mongoclient.server_info()
        if isinstance(server_info, dict) and 'ok' in server_info and server_info['ok'] == 1:
            """Connected to MongoDB"""
            database: MongoDatabase = mongoclient[MONGO_BILLING_DATABASE]
            database_info = database.command("buildinfo")
            if isinstance(database_info, dict) and 'ok' in database_info and database_info['ok'] == 1:
                """database exists"""
                collection: MongoCollection = database[MONGO_BILLING_COLLECTION]
                updateresult = collection.update_one(
                    {"_id": user_id}, {'$inc': {f"{MONGO_BILLING_FIELD}": amount}})

                if updateresult.modified_count == 1:
                    """User has been charged"""
                    # Return ESME_ROK
                    return 0
                else:
                    """User has not been charged"""
                    # Return ESME_RTHROTTLED
                    return 88
            else:
                """database does not exist"""
                # Return ESME_RDELIVERYFAILURE
                return 254
        else:
            """Could not connect to MongoDB"""
            # Return ESME_RDELIVERYFAILURE
            return 254

    except Exception:
        # We got an error when calling for charging
        # Return ESME_RDELIVERYFAILURE
        return 254

    except MongoErrors:
        # We got an error when calling for charging
        # Return ESME_RDELIVERYFAILURE
        return 254


_pdu = routable.pdu
amount = -1
while hasattr(_pdu, 'nextPdu'):
    _pdu = _pdu.nextPdu
    amount -= 1

if 'source_add' not in routable.pdu.params:
    smpp_status = charge_MT(routable.user.uid, amount)
