import os
from .mongodb import MongoDB
import logging

class ConfigurationStreamer:
    def __init__(
            self, 
            mongo_connection_string: str, 
            configuration_database: str, 
            sync_current_first:bool=True, 
            jasmin_cli_host: str = "127.0.0.1", 
            jasmin_cli_port: int = 8990, 
            jasmin_cli_timeout: int = 30, 
            jasmin_cli_auth: bool = True, 
            jasmin_cli_username: str = "jcliadmin", 
            jasmin_cli_password: str = "jclipwd", 
            jasmin_cli_standard_prompt: str = "jcli : ", 
            jasmin_cli_interactive_prompt: str = "> ", 
            logPath: str = "/var/log"
        ):
        
        self.MONGODB_CONNECTION_STRING = mongo_connection_string
        
        self.MONGODB_MODULES_DATABASE = configuration_database

        self.SYNC_CURRENT_FIRST = sync_current_first
        
        self.telnet_config: dict = {
            "host": jasmin_cli_host,
            "port": jasmin_cli_port,
            "timeout": jasmin_cli_timeout,
            "auth": jasmin_cli_auth,
            "username": jasmin_cli_username,
            "password": jasmin_cli_password,
            "standard_prompt": jasmin_cli_standard_prompt,
            "interactive_prompt": jasmin_cli_interactive_prompt
        }
        
        logFormatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

        fileHandler = logging.FileHandler(
            f"{logPath.rstrip('/')}/jasmin_mongo_configuration.log")
        fileHandler.setLevel(logging.DEBUG)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)


    def startStream(self):

        logging.info("*********************************************")
        logging.info("::Jasmin MongoDB Configuration::")
        logging.info("")
        
        mongosource = MongoDB(connection_string=self.MONGODB_CONNECTION_STRING,
                              database_name=self.MONGODB_MODULES_DATABASE)
        if mongosource.startConnection() is True:
            mongosource.stream(
                telnet_config=self.telnet_config, syncCurrentFirst=self.SYNC_CURRENT_FIRST)


def startFromConsole():
    if os.getenv("JASMIN_CLI_HOST") is None or os.getenv("MONGODB_CONNECTION_STRING") is None or os.getenv("MONGODB_MODULES_DATABASE") is None:
        logging.info(
            "Sorry, Could not find correct ENVIRONMENT variables!")
        logging.info("Please export the fallowing:                          \n\
            JASMIN_CLI_HOST                         =       **NoDefault**   \n\
            JASMIN_CLI_PORT                         =           8990        \n\
            JASMIN_CLI_TIMEOUT                      =           30          \n\
            JASMIN_CLI_AUTH                         =           True        \n\
            JASMIN_CLI_USERNAME                     =         jcliadmin     \n\
            JASMIN_CLI_PASSWORD                     =         jclipwd       \n\
            JASMIN_CLI_STANDARD_PROMPT              =         \"jcli : \"   \n\
            JASMIN_CLI_INTERACTIVE_PROMPT           =           \"> \"      \n\
            MONGODB_CONNECTION_STRING               =       **NoDefault**   \n\
            MONGODB_MODULES_DATABASE                =       **NoDefault**   \n\
            SYNC_CURRENT_FIRST                      =           True        \n\
            JASMIN_MONGO_CONFIGURATION_LOG_PATH     =         /var/log      ")

    configurationStreamer = ConfigurationStreamer(
        mongo_connection_string=os.getenv("MONGODB_CONNECTION_STRING"), 
        configuration_database=os.getenv("MONGODB_MODULES_DATABASE"),
        sync_current_first=bool(os.getenv("SYNC_CURRENT_FIRST", 'True').lower() in ['true', 'y', 'yes', '1']),
        jasmin_cli_host=os.getenv("JASMIN_CLI_HOST"),
        jasmin_cli_port=int(os.getenv("JASMIN_CLI_PORT", "8990")),
        jasmin_cli_timeout=int(os.getenv("JASMIN_CLI_TIMEOUT", "30")),
        jasmin_cli_auth=bool(os.getenv("JASMIN_CLI_AUTH", 'True').lower() in ['true', 'y', 'yes', '1']),
        jasmin_cli_username=os.getenv("JASMIN_CLI_USERNAME", "jcliadmin"),
        jasmin_cli_password=os.getenv("JASMIN_CLI_PASSWORD", "jclipwd"),
        jasmin_cli_standard_prompt=os.getenv("JASMIN_CLI_STANDARD_PROMPT", "jcli : "),
        jasmin_cli_interactive_prompt=os.getenv("JASMIN_CLI_INTERACTIVE_PROMPT", "> "),
        logPath=os.getenv("JASMIN_MONGO_CONFIGURATION_LOG_PATH", "/var/log")
    )

    configurationStreamer.startStream()
