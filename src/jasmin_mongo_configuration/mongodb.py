import logging

import pkg_resources
from jasmin_telnet.proxy import Proxy as JasminTelnetProxy
from pymongo import MongoClient
from pymongo import errors as MongoErrors
from pymongo.database import Database as MongoDatabase

from jasmin_mongo_configuration.defaults import *


class MongoDB:

    def __init__(self, connection_string, database_name):
        """ Constructor """
        self.connection_string = connection_string
        self.database_name = database_name
        self.cli_conn: dict = {}
        logging.info("Starting MongoDB cluster's connection")

    def logger_callback(self, msg: str):
        logging.info(msg=msg)

    def startConnection(self) -> bool:
        mongoclient = MongoClient(self.connection_string)
        server_info = mongoclient.server_info()
        if isinstance(server_info, dict) and 'ok' in server_info and server_info['ok'] == 1:
            logging.info("Connected to MongoDB")
            self.mongoclient = mongoclient
            adminDatabase: MongoDatabase = self.mongoclient['admin']
            database: MongoDatabase = self.mongoclient[self.database_name]
            adminDatabase_info = adminDatabase.command("buildinfo")
            database_info = database.command("buildinfo")
            if isinstance(adminDatabase_info, dict) and isinstance(database_info, dict) and \
                    'ok' in adminDatabase_info and 'ok' in database_info and \
                    adminDatabase_info['ok'] == 1 and database_info['ok'] == 1:
                clusterParameter = adminDatabase.command(
                    {'getClusterParameter': "changeStreamOptions"})
                preAndPostImagesExpireAfterSeconds = clusterParameter[
                    'clusterParameters'][0]['preAndPostImages']['expireAfterSeconds']
                if isinstance(preAndPostImagesExpireAfterSeconds, int) is False or preAndPostImagesExpireAfterSeconds == 0:
                    logging.info("")
                    logging.info("Detected Pre and Post Images is not active")
                    adminDatabase.command({
                        'setClusterParameter':
                        {'changeStreamOptions': {
                            'preAndPostImages': {'expireAfterSeconds': 100}}}
                    })
                    logging.info(
                        "Cluster Parameters changed to support Pre and Post Images for 100 seconds")
                else:
                    logging.info("")
                    logging.info(
                        f"Cluster Parameters support Pre and Post Images for {preAndPostImagesExpireAfterSeconds} seconds")

                logging.info("")

                logging.info(f"Set to use database: {self.database_name}")
                logging.info("")
                self.adminDatabase = adminDatabase
                self.database = database
                return True
            else:
                logging.critical(
                    f"Failed to use database: {self.database_name}")
                return False
        else:
            logging.critical("Failed to connect to MongoDB")
            return False

    def set_bill_managment_state(self, state: bool):
        self.bill_managment: bool = state

    def get_bill_managment_state(self) -> bool:
        return hasattr(self, "bill_managment") and isinstance(self.bill_managment, bool) and self.bill_managment is True

    def get_one_module(self, module: str) -> dict[str, str | float | bool]:
        "" ""
        data: dict[str, str | float | bool] = {}
        cursor = self.database[module].find()
        for row in cursor:
            sub_id = row["_id"]
            del row["_id"]
            data[sub_id] = row

        return data

    def get_one_submodule(self, module: str, sub_id: str) -> dict[str, str | float | bool]:
        "" ""
        return self.database[module].find_one({"_id": sub_id})

    def insert_one(self, module, sub_id, data):
        data["_id"] = sub_id
        self.database[module].insert_one(data)

    def increment_one(self, module, sub_id, data):
        self.database[module].update_one(
            {"_id": sub_id}, {'$inc': data})

    def update_one(self, module, sub_id, data, upsert=True):
        self.database[module].update_one(
            {"_id": sub_id}, {'$set': data}, upsert=upsert)

    def pullAllConfigurations(self):
        "" ""
        modules_to_sync = ["smppccm", "httpccm", "group", "user", "filter",
                           "mointerceptor", "mtinterceptor", "morouter", "mtrouter"]

        logging.info(
            "Synchronizing all configuration to Jasmin from MongoDB cluster. Applies to:")
        for module in modules_to_sync:
            sub_data: dict = {}
            cursor = self.database[module].find()

            for row in cursor:
                if self.get_bill_managment_state() is True:
                    if module == "user":
                        row["mt_messaging_cred quota balance"] = "None"
                        row["mt_messaging_cred quota sms_count"] = "None"

                sub_id = row["_id"]
                del row["_id"]
                sub_data[sub_id] = row

            self.stream_handler(
                payload={
                    "change_type": "sync",
                    "module": module,
                    "sub_data": sub_data
                })

        logging.info("Finished applying configurations")

    def stream(
        self,
        cli_host: str = DEFAULT_CLI_HOST,
        cli_port: int = DEFAULT_CLI_PORT,
        cli_timeout: int = DEFAULT_CLI_TIMEOUT,
        cli_auth: bool = DEFAULT_CLI_AUTH,
        cli_username: str = DEFAULT_CLI_USERNAME,
        cli_password: str = DEFAULT_CLI_PASSWORD,
        cli_standard_prompt: str = DEFAULT_CLI_STANDARD_PROMPT,
        cli_interactive_prompt: str = DEFAULT_CLI_INTERACTIVE_PROMPT,
        syncCurrentFirst: bool = False
    ):

        self.cli_conn: dict = {
            "host": cli_host,
            "port": cli_port,
            "timeout": cli_timeout,
            "auth": cli_auth,
            "username": cli_username,
            "password": cli_password,
            "standard_prompt": cli_standard_prompt,
            "interactive_prompt": cli_interactive_prompt
        }

        try:
            with self.database.watch(full_document='updateLookup') as stream:
                if self.get_bill_managment_state() is True:
                    logging.info("Bill managment Enabled!")
                    logging.warn("Need to install interceptors manually!")
                    logging.info(
                        "For the MT Interceptor blueprint, please use the following command:")
                    logging.info(
                        "jasminmongoconfd -get-interceptor mt > mtinterceptor.py")
                    logging.info(
                        "For the MO Interceptor blueprint, please use the following command:")
                    logging.info(
                        "jasminmongoconfd -get-interceptor mo > mointerceptor.py")
                    logging.info(
                        "Then, please edit & copy the files to the jasmin's server manually and then add the Interceptors to the jasmin's config collection")
                    logging.info(" ")

                if syncCurrentFirst is True:
                    # Sync current data to Jasmin before waiting for changes
                    logging.info("Sync current configuration first is ENABLED")
                    self.pullAllConfigurations()
                    logging.info("")
                else:
                    logging.info(
                        "Sync current configuration first is DISABLED")
                    logging.info(
                        "Skipping synchronizing current configurations")
                    logging.info("")

                logging.info("Starting MongoDB cluster's Change Stream")
                logging.info("")
                for change in stream:
                    module = change["ns"]["coll"]
                    sub_id = change["documentKey"]["_id"]
                    change_type = change["operationType"]
                    if change_type == "invalidate":
                        return
                    if change_type in ["create", "drop", "dropDatabase", "rename", "modify"]:
                        logging.warn(
                            "Received a strange structure change. Ignoring stream content!!!!")
                        continue
                    if "updateDescription" in change and module in ["user", "smppccm"]:
                        sub_data = change["updateDescription"]["updatedFields"]
                    elif "fullDocument" in change:
                        sub_data = change["fullDocument"]
                    else:
                        sub_data = {}

                    if self.get_bill_managment_state() is True and module == "user":
                        if isinstance(sub_data, dict) and "mt_messaging_cred quota balance" in sub_data:
                            del sub_data["mt_messaging_cred quota balance"]
                        if isinstance(sub_data, dict) and "mt_messaging_cred quota sms_count" in sub_data:
                            del sub_data["mt_messaging_cred quota sms_count"]

                    if isinstance(sub_data, dict) and "_id" in sub_data:
                        del sub_data["_id"]

                    if not change_type == "delete" and len(sub_data.keys()) < 1:
                        continue

                    logging.info(
                        "Recieved notice of change in configurations from MongoDB cluster. Applies to:")
                    self.stream_handler(
                        payload={
                            "module": module,
                            "sub_id": sub_id,
                            "change_type": change_type,
                            "sub_data": sub_data
                        }
                    )
                    logging.info("Finished applying configurations")

        except MongoErrors.PyMongoError as err:
            # The ChangeStream encountered an unrecoverable error or the
            # resume attempt failed to recreate the cursor.
            logging.error(err)
            pass
        except KeyboardInterrupt:
            pass

    def stream_handler(self, payload):
        """Handle callback for jasmin stream"""
        jasmin_proxy = JasminTelnetProxy(
            host=self.cli_conn.get("host", DEFAULT_CLI_HOST),
            port=self.cli_conn.get("port", DEFAULT_CLI_PORT),
            timeout=self.cli_conn.get("timeout", DEFAULT_CLI_TIMEOUT),
            auth=self.cli_conn.get("auth", DEFAULT_CLI_AUTH),
            username=self.cli_conn.get("username", DEFAULT_CLI_USERNAME),
            password=self.cli_conn.get("password", DEFAULT_CLI_PASSWORD),
            standard_prompt=self.cli_conn.get(
                "standard_prompt", DEFAULT_CLI_STANDARD_PROMPT),
            interactive_prompt=self.cli_conn.get(
                "interactive_prompt", DEFAULT_CLI_INTERACTIVE_PROMPT),
            log_status=True,
            logger=self.logger_callback
        )

        if payload["change_type"] == "sync":
            """ Sync """
            jasmin_proxy.sync(
                module=payload["module"],
                sub_modules_data=payload["sub_data"]
            )

        if payload["change_type"] == "insert":
            """ Add """
            jasmin_proxy.add(
                module=payload["module"],
                sub_id=payload["sub_id"],
                options=payload["sub_data"]
            )

        if payload["change_type"] in ["update", "replace"]:
            """ Edit """
            jasmin_proxy.edit(
                module=payload["module"],
                sub_id=payload["sub_id"],
                options=payload["sub_data"]
            )

        if payload["change_type"] == "delete":
            """ Remove """
            jasmin_proxy.remove(
                module=payload["module"],
                sub_id=payload["sub_id"]
            )
