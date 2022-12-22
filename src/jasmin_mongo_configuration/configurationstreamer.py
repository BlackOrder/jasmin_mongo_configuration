import logging
import os

import pkg_resources

from .mongodb import MongoDB

NODEFAULT: str = "REQUIRED: NO_DEFAULT"
DEFAULT_SYNC_CURRENT_FIRST: bool = True
DEFAULT_JASMIN_CLI_HOST: str = '127.0.0.1'
DEFAULT_JASMIN_CLI_PORT: int = 8990
DEFAULT_JASMIN_CLI_TIMEOUT: int = 30
DEFAULT_JASMIN_CLI_AUTH: bool = True
DEFAULT_JASMIN_CLI_USERNAME: str = "jcliadmin"
DEFAULT_JASMIN_CLI_PASSWORD: str = "jclipwd"
DEFAULT_JASMIN_CLI_STANDARD_PROMPT: str = "jcli : "
DEFAULT_JASMIN_CLI_INTERACTIVE_PROMPT: str = "> "
DEFAULT_LOG_PATH: str = "/var/log/jasmin/"
DEFAULT_LOG_LEVEL: str = "INFO"


class ConfigurationStreamer:
    def __init__(
        self,
        mongo_connection_string: str,
        configuration_database: str,
        sync_current_first: bool = DEFAULT_SYNC_CURRENT_FIRST,
        jasmin_cli_host: str = DEFAULT_JASMIN_CLI_HOST,
        jasmin_cli_port: int = DEFAULT_JASMIN_CLI_PORT,
        jasmin_cli_timeout: int = DEFAULT_JASMIN_CLI_TIMEOUT,
        jasmin_cli_auth: bool = DEFAULT_JASMIN_CLI_AUTH,
        jasmin_cli_username: str = DEFAULT_JASMIN_CLI_USERNAME,
        jasmin_cli_password: str = DEFAULT_JASMIN_CLI_PASSWORD,
        jasmin_cli_standard_prompt: str = DEFAULT_JASMIN_CLI_STANDARD_PROMPT,
        jasmin_cli_interactive_prompt: str = DEFAULT_JASMIN_CLI_INTERACTIVE_PROMPT,
        logPath: str = DEFAULT_LOG_PATH,
        logLevel: str = DEFAULT_LOG_LEVEL
    ):

        self.MONGO_CONNECTION_STRING = mongo_connection_string

        self.MONGO_CONFIGURATION_DATABASE = configuration_database

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
        rootLogger.setLevel(logLevel)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logLevel)
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

        if not os.path.exists(logPath):
            os.makedirs(logPath)

        fileHandler = logging.FileHandler(
            f"{logPath.rstrip('/')}/jasmin_mongo_configuration.log")
        fileHandler.setLevel(logLevel)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

    def start(self):

        logging.info("*********************************************")
        logging.info("::Jasmin MongoDB Configuration::")
        logging.info("")

        mongosource = MongoDB(connection_string=self.MONGO_CONNECTION_STRING,
                              database_name=self.MONGO_CONFIGURATION_DATABASE)
        if mongosource.startConnection() is True:
            mongosource.stream(
                telnet_config=self.telnet_config, syncCurrentFirst=self.SYNC_CURRENT_FIRST)


def startFromCLI():
    import argparse
    parser = argparse.ArgumentParser(
        description=f"Jasmin MongoDB Configuration, Links Jasmin SMS Gateway to MongoDB cluster's Change Stream (can be one node).")
    
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {pkg_resources.get_distribution("jasmin_mongo_configuration").version}')

    parser.add_argument('--connection-string', '-c', type=str, dest='mongo_connection_string',
        help='MongoDB Connection String, (Default: ** Required **). ex. mongodb://mongoroot:mongopass@mongodb1:27017,mongodb2:27017,mongodb3:27017/?authSource=admin&replicaSet=rs',
        required=os.getenv("MONGO_CONNECTION_STRING") is None,
        default=os.getenv("MONGO_CONNECTION_STRING"))
    
    parser.add_argument('--configuration-database', '-db', type=str, dest='configuration_database',
        help='Configuration Database, (Default: ** Required **). MongoDB database name where you have saved the jasmin configurations',
        required=os.getenv("MONGO_CONFIGURATION_DATABASE") is None,
        default=os.getenv("MONGO_CONFIGURATION_DATABASE"))
    
    parser.add_argument('--sync-current-first', '-sync', type=bool, dest='sync_current_first',
        help=f'Sync current configuration first, (Default: {"Enabled" if DEFAULT_SYNC_CURRENT_FIRST else "Disabled"}). if enabled, will sync the current configurations first before monitoring for any changes',
        choices=['yes', 'y', 'no', 'n'],
        required=False,
        default=bool(os.getenv("SYNC_CURRENT_FIRST", 'yes' if DEFAULT_SYNC_CURRENT_FIRST else 'no').lower() in ['yes', 'y']))
    
    parser.add_argument('--cli-host', '-H', type=str, dest='jasmin_cli_host',
        help=f'Jasmin CLI Host, (Default: "{DEFAULT_JASMIN_CLI_HOST}"). The hostname of the jasmin server',
        required=False,
        default=os.getenv("JASMIN_CLI_HOST", DEFAULT_JASMIN_CLI_HOST))
    
    parser.add_argument('--cli-port', '-P', type=int, dest='jasmin_cli_port',
        help=f'Jasmin CLI Port, (Default: "{DEFAULT_JASMIN_CLI_PORT}"). The port of the jasmin server cli',
        required=False,
        default=int(os.getenv("JASMIN_CLI_PORT", DEFAULT_JASMIN_CLI_PORT)))
    
    parser.add_argument('--cli-timeout', '-t', type=int, dest='jasmin_cli_timeout',
        help=f'Jasmin CLI Timeout, (Default: "{DEFAULT_JASMIN_CLI_TIMEOUT}"). The timeout for the CLI connection. Should be increased if your network is not stable.',
        required=False,
        default=int(os.getenv("JASMIN_CLI_TIMEOUT", DEFAULT_JASMIN_CLI_TIMEOUT)))
    
    parser.add_argument('--cli-auth', '-a', type=bool, dest='jasmin_cli_auth',
        help=f'Jasmin CLI Auth, (Default: {"Enabled" if DEFAULT_JASMIN_CLI_AUTH else "Disabled"}). if enabled, will use authentication for the telnet connection.',
        choices=['yes', 'y', 'no', 'n'],
        required=False,
        default=bool(os.getenv("JASMIN_CLI_AUTH", 'yes' if DEFAULT_JASMIN_CLI_AUTH else 'no').lower() in ['yes', 'y']))
    
    parser.add_argument('--cli-username', '-u', type=str, dest='jasmin_cli_username',
        help=f'Jasmin CLI Username, (Default: "{DEFAULT_JASMIN_CLI_USERNAME}"). The jasmin telnet cli username',
        required=False,
        default=os.getenv("JASMIN_CLI_USERNAME", DEFAULT_JASMIN_CLI_USERNAME))
    
    parser.add_argument('--cli-password', '-p', type=str, dest='jasmin_cli_password',
        help=f'Jasmin CLI Password, (Default: "{DEFAULT_JASMIN_CLI_PASSWORD}"). The jasmin telnet cli password',
        required=False,
        default=os.getenv("JASMIN_CLI_PASSWORD", DEFAULT_JASMIN_CLI_PASSWORD))
    
    parser.add_argument('--cli-standard-prompt', type=str, dest='jasmin_cli_standard_prompt',
        help=f'Jasmin CLI Standard Prompt, (Default: "{DEFAULT_JASMIN_CLI_STANDARD_PROMPT}"). There shouldn\'t be a need to change this.',
        required=False,
        default=os.getenv("JASMIN_CLI_STANDARD_PROMPT", DEFAULT_JASMIN_CLI_STANDARD_PROMPT))
    
    parser.add_argument('--cli-interactive-prompt', type=str, dest='jasmin_cli_interactive_prompt',
        help=f'Jasmin CLI Interactive Prompt, (Default: "{DEFAULT_JASMIN_CLI_INTERACTIVE_PROMPT}"). There shouldn\'t be a need to change this.',
        required=False,
        default=os.getenv("JASMIN_CLI_INTERACTIVE_PROMPT", DEFAULT_JASMIN_CLI_INTERACTIVE_PROMPT))
    
    parser.add_argument('--log-path', type=str, dest='logPath',
        help=f'Log Path, (Default: "{DEFAULT_LOG_PATH}")',
        required=False,
        default=os.getenv("JASMIN_MONGO_CONFIGURATION_LOG_PATH", DEFAULT_LOG_PATH))
    
    parser.add_argument('--log-level', type=str, dest='logLevel',
        help=f'Log Level, (Default: "{DEFAULT_LOG_LEVEL}")',
        required=False,
        default=os.getenv("JASMIN_MONGO_CONFIGURATION_LOG_LEVEL", DEFAULT_LOG_LEVEL))

    configurationstreamer = ConfigurationStreamer(**vars(parser.parse_args()))

    configurationstreamer.start()
