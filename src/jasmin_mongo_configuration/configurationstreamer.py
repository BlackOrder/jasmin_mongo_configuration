import argparse
import logging
import os

import pkg_resources

from jasmin_mongo_configuration.mongodb import MongoDB
from jasmin_mongo_configuration.defaults import *


class ConfigurationStreamer:
    def __init__(
        self,
        mongo_connection_string: str,
        configuration_database: str,
        sync_current_first: bool = DEFAULT_SYNC_CURRENT_FIRST,
        bill_managment: bool = DEFAULT_BILL_MANAGMENT,
        cli_host: str = DEFAULT_CLI_HOST,
        cli_port: int = DEFAULT_CLI_PORT,
        cli_timeout: int = DEFAULT_CLI_TIMEOUT,
        cli_auth: bool = DEFAULT_CLI_AUTH,
        cli_username: str = DEFAULT_CLI_USERNAME,
        cli_password: str = DEFAULT_CLI_PASSWORD,
        cli_standard_prompt: str = DEFAULT_CLI_STANDARD_PROMPT,
        cli_interactive_prompt: str = DEFAULT_CLI_INTERACTIVE_PROMPT,
        logPath: str = DEFAULT_LOG_PATH,
        logLevel: str = DEFAULT_LOG_LEVEL
    ):

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

        logging.info("*********************************************")
        logging.info("::Jasmin MongoDB Configuration::")
        logging.info("")

        mongosource = MongoDB(
            connection_string=mongo_connection_string,
            database_name=configuration_database
        )
        if mongosource.startConnection() is True:
            mongosource.set_bill_managment_state(bill_managment)
            mongosource.stream(
                cli_host=cli_host,
                cli_port=cli_port,
                cli_timeout=cli_timeout,
                cli_auth=cli_auth,
                cli_username=cli_username,
                cli_password=cli_password,
                cli_standard_prompt=cli_standard_prompt,
                cli_interactive_prompt=cli_interactive_prompt,
                syncCurrentFirst=sync_current_first
            )


def str2bool(v: str) -> bool:
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'y', 'true', 't', '1'):
        return True
    elif v.lower() in ('no', 'n', 'false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def startFromCLI():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description=f"Jasmin MongoDB Configuration, Links Jasmin SMS Gateway to MongoDB cluster's Change Stream (can be one node).")

    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'%(prog)s {pkg_resources.get_distribution("jasmin_mongo_configuration").version}',
                        help="\n".join([
                            'Show version',
                            ' '
                        ]))

    mongoConfigurationsParserGroup = parser.add_argument_group(
        title='MongoDB',
        description="\n".join([
            'MongoDB cluster (can be one node) connection configuration section. You can use environment variables instead of command line arguments.',
        ]))
    mongoConfigurationsParserGroup.add_argument('-c',
                                                type=str,
                                                dest='mongo_connection_string',
                                                metavar='$connection_string',
                                                required=os.getenv(
                                                    "MONGO_CONNECTION_STRING") is None,
                                                default=os.getenv(
                                                    "MONGO_CONNECTION_STRING"),
                                                help="\n".join([
                                                    'MongoDB Connection String (Default: ** Required **)',
                                                    'Alternatively: You can use environment variable MONGO_CONNECTION_STRING',
                                                    'Example: mongodb://mongoroot:mongopass@mongodb1:27017,mongodb2:27017,mongodb3:27017/?authSource=admin&replicaSet=rs',
                                                    'MongoDB connection string to connect to the cluster',
                                                    ' '
                                                ]))

    mongoConfigurationsParserGroup.add_argument('-db',
                                                type=str,
                                                dest='configuration_database',
                                                metavar='$database_name',
                                                required=os.getenv(
                                                    "MONGO_CONFIGURATION_DATABASE") is None,
                                                default=os.getenv(
                                                    "MONGO_CONFIGURATION_DATABASE"),
                                                help="\n".join([
                                                    'Configuration Database (Default: ** Required **)',
                                                    'Alternatively: You can use environment variable MONGO_CONFIGURATION_DATABASE',
                                                    'MongoDB database name where you have saved the jasmin configurations',
                                                    ' '
                                                ]))

    appConfigurationsParserGroup = parser.add_argument_group(
        title='Features',
        description="\n".join([
            'Application features section. You can enable or disable them. You can use environment variables instead of command line arguments.',
        ]))
    appConfigurationsParserGroup.add_argument('-sync',
                                              type=str2bool,
                                              dest='sync_current_first',
                                              metavar='$is_start_sync',
                                              required=False,
                                              default=bool(os.getenv("SYNC_CURRENT_FIRST", 'yes' if DEFAULT_SYNC_CURRENT_FIRST else 'no').lower(
                                              ) in ['yes', 'true', 't', 'y', '1']),
                                              help="\n".join([
                                                  f'Sync current configuration first (Default: {"Enabled" if DEFAULT_SYNC_CURRENT_FIRST else "Disabled"})',
                                                  'Options: [Enable (true, t, yes, y, 1) and Disable (false, f, no, n, 0)]',
                                                  'Alternatively: You can use environment variable SYNC_CURRENT_FIRST'
                                                  'When enabled, will sync the current configurations first before monitoring for any changes',
                                                  ' '
                                              ]))

    appConfigurationsParserGroup.add_argument('-bill',
                                              type=str2bool,
                                              dest='bill_managment',
                                              metavar='$is_bill_managment',
                                              required=False,
                                              default=bool(os.getenv("JASMIN_MONGO_CONFIGURATION_BILL_MANAGMENT",
                                                                     'yes' if DEFAULT_BILL_MANAGMENT else 'no').lower() in ['yes', 'y']),
                                              help="\n".join([
                                                  f'Bill Managment (Default: {"Enabled" if DEFAULT_BILL_MANAGMENT else "Disabled"})',
                                                  'Options: [Enable (true, t, yes, y, 1) and Disable (false, f, no, n, 0)]',
                                                  'Alternatively: You can use environment variable JASMIN_MONGO_CONFIGURATION_BILL_MANAGMENT',
                                                  'When enabled, the "mt_messaging_cred quota balance" and "mt_messaging_cred quota sms_count" fields in the `user` module',
                                                  'will be ignored by the Change Stream. Then a special mt/mo interceptors will be installed in jasmin to check for billable messages',
                                                  'and will be used to bill users.',
                                                  ' '
                                              ]))

    jasminParserGroup = parser.add_argument_group(
        title='Jasmin Connection',
        description="\n".join([
            'Jasmin Connection Configurations. You can use the environment variables to set the values instead of command line arguments.',
        ]))
    jasminParserGroup.add_argument('-H',
                                                 type=str,
                                   dest='cli_host',
                                                 metavar='$host',
                                                 required=False,
                                                 default=os.getenv(
                                       "JASMIN_CLI_HOST", DEFAULT_CLI_HOST),
                                                 help="\n".join([
                                                     f'Jasmin Host (Default: "%(default)s")',
                                       'Alternatively: You can use environment variable JASMIN_CLI_HOST',
                                                     'The hostname of the jasmin server',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-P',
                                                 type=int,
                                                 dest='cli_port',
                                                 metavar='$port',
                                                 required=False,
                                                 default=int(
                                                     os.getenv("JASMIN_CLI_PORT", DEFAULT_CLI_PORT)),
                                                 help="\n".join([
                                                     f'Jasmin CLI Port (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_PORT',
                                                     'The port of the jasmin server cli',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-t',
                                                 type=int,
                                                 dest='cli_timeout',
                                                 metavar='$timeout',
                                                 required=False,
                                                 default=int(
                                                     os.getenv("JASMIN_CLI_TIMEOUT", DEFAULT_CLI_TIMEOUT)),
                                                 help="\n".join([
                                                     f'Jasmin CLI Timeout (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_TIMEOUT',
                                                     'The timeout for the CLI connection. Should be increased if your network is not stable.',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-standard-prompt',
                                                 type=str,
                                                 dest='cli_standard_prompt',
                                                 metavar='$standard_prompt',
                                                 required=False,
                                                 default=os.getenv(
                                                     "JASMIN_CLI_STANDARD_PROMPT", DEFAULT_CLI_STANDARD_PROMPT),
                                                 help="\n".join([
                                                     f'Jasmin CLI Standard Prompt (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_STANDARD_PROMPT',
                                                     'There shouldn\'t be a need to change this.',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-interactive-prompt',
                                                 type=str,
                                                 dest='cli_interactive_prompt',
                                                 metavar='$interactive_prompt',
                                                 required=False,
                                                 default=os.getenv(
                                                     "JASMIN_CLI_INTERACTIVE_PROMPT", DEFAULT_CLI_INTERACTIVE_PROMPT),
                                                 help="\n".join([
                                                     f'Jasmin CLI Interactive Prompt (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_INTERACTIVE_PROMPT',
                                                     'There shouldn\'t be a need to change this.',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-auth',
                                                 type=str2bool,
                                                 dest='cli_auth',
                                                 metavar='$is_auth',
                                                 required=False,
                                                 default=bool(os.getenv(
                                                     "JASMIN_CLI_AUTH", 'yes' if DEFAULT_CLI_AUTH else 'no').lower() in ['yes', 'y']),
                                                 help="\n".join([
                                                     f'Jasmin CLI Auth (Default: {"Enabled" if DEFAULT_CLI_AUTH else "Disabled"})',
                                                     'Options: [Enable (true, t, yes, y, 1) and Disable (false, f, no, n, 0)]',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_AUTH',
                                                     'When enabled, will use authentication for the telnet connection.',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-u',
                                                 type=str,
                                                 dest='cli_username',
                                                 metavar='$username',
                                                 required=False,
                                                 default=os.getenv(
                                                     "JASMIN_CLI_USERNAME", DEFAULT_CLI_USERNAME),
                                                 help="\n".join([
                                                     f'Jasmin CLI Username (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_USERNAME',
                                                     'The jasmin telnet cli username',
                                                     ' '
                                                 ]))

    jasminParserGroup.add_argument('-p',
                                                 type=str,
                                                 dest='cli_password',
                                                 metavar='$password',
                                                 required=False,
                                                 default=os.getenv(
                                                     "JASMIN_CLI_PASSWORD", DEFAULT_CLI_PASSWORD),
                                                 help="\n".join([
                                                     f'Jasmin CLI Password (Default: "%(default)s")',
                                                     'Alternatively: You can use environment variable JASMIN_CLI_PASSWORD',
                                                     'The jasmin telnet cli password',
                                                     ' '
                                                 ]))

    loggingConfigsParserGroup = parser.add_argument_group(
        title='Logging',
        description="\n".join([
            'Logging Configurations. You can use the environment variables to set the values instead of command line arguments.',
        ]))
    loggingConfigsParserGroup.add_argument('--log-path',
                                           type=str,
                                           dest='logPath',
                                           metavar='$path',
                                           required=False,
                                           default=os.getenv(
                                               "JASMIN_MONGO_CONFIGURATION_LOG_PATH", DEFAULT_LOG_PATH),
                                           help="\n".join([
                                               f'Log Path (Default: "%(default)s")',
                                               'Alternatively: You can use environment variable JASMIN_MONGO_CONFIGURATION_LOG_PATH',
                                               ' '
                                           ]))

    loggingConfigsParserGroup.add_argument('--log-level',
                                           type=str,
                                           dest='logLevel',
                                           metavar='$level',
                                           required=False,
                                           default=os.getenv(
                                               "JASMIN_MONGO_CONFIGURATION_LOG_LEVEL", DEFAULT_LOG_LEVEL),
                                           help="\n".join([
                                               f'Log Level (Default: "%(default)s")',
                                               'Alternatively: You can use environment variable JASMIN_MONGO_CONFIGURATION_LOG_LEVEL',
                                               ' '
                                           ]))

    configurationstreamer = ConfigurationStreamer(**vars(parser.parse_args()))

    configurationstreamer.start()
