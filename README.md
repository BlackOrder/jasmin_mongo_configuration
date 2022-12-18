# Jasmin Mongo Configuration

Links [Jasmin SMS Gateway](https://github.com/jookies/jasmin)'s configuration to MongoDB cluster stream (can be a one-node cluster). This package is using MongoDB cluster [Change Stream](https://www.mongodb.com/docs/manual/changeStreams/) which allow applications to access real-time data changes.


### Table of Contents
1. **[Installation Instructions](#installation-instructions)**<br>
    + **[PYPI](#pypi)**<br>
    + **[From Source](#from-source)**<br>
2. **[Setup MongoDB CLuster](#setup-mongodb-cluster)**<br>
    + **[Docker](#docker)**<br>
        * **[Prepare network](#prepare-network)**<br>
        * **[Prepare variables](#prepare-variables)**<br>
        * **[Create cluster key](#create-cluster-key)**<br>
            1. **[One line](#one-line)**<br>
            2. **[Manually](#manually)**<br>
        * **[Start MongoDB cluster service](#start-mongodb-cluster-service)**<br>
3. **[Usage Instructions](#usage-instructions)**<br>
    + **[Data Structure](#data-structure)**<br>
    + **[Start the Service](#start-the-service)**<br>
        * **[Set variables](#set-variables)**<br>
        * **[Start Change Stream](#start-change-stream)**<br>


## Installation Instructions
### PYPI:
```
pip3 install -U jasmin-mongo-configuration
```
### From Source:
```
git clone https://github.com/BlackOrder/jasmin_mongo_configuration.git
cd jasmin_mongo_configuration
pip3 install .
```

## Setup MongoDB CLuster
### Docker
#### Prepare network:
```
docker network create mongo_cluster_subnet
```

#### Prepare variables:
```
cd docker
cp .env.example .env
```
Edit the `.env` file. change the default username and password.

#### Create cluster key:
##### One line:
```
echo "MONGODB_CLUSTER_KEY="$(openssl rand -base64 756 | sed -z 's/\n/\\n/g') >> .env
```
if the above failes to create the env variable in `.env` file, you have to do it in multiple steps.


##### Manually
1. Create key file:
```
openssl rand -base64 756 > mongo_cluster_key
```

2. Edit Key:
```
vim ./mongo_cluster_key
```
replace all new-line with `\n`

3. Step 3:
Create a variable in `.env` file and use the string from `Step 2` as it's value
```
MONGODB_CLUSTER_KEY=####-Single line encrypted key-####
```

#### Start MongoDB cluster service:
```
docker compose -f docker-compose.MongoCluster.yml up -d
```


## Usage Instructions:
`Jasmin Mongo Configuration` sync all configurations [`Smppccm`, `Httpccm`, `Group`, `User`, `Filter`, `MoRouter`, `MtRouter`, `MoInterceptor`, and `MtInterceptor`] from a MongoDB cluster to a `jasmin` instance. All settings are read from OS ENV when run from console. if you want to import it in you code, you can supply the settings on initialization.

### Data Structure
The Database supplied should have a collection for each module:
```
smppccm
group
user
filter
httpccm
morouter
mointerceptor
mtrouter
mtinterceptor
```
Each collection should contains your desired `jasmin`'s settings in a key value format. and should have a valid format for Jasmin. for example the `user` collection should have documents in this format:
```
{
    '_id': '$UID',
    'gid': '$GID',
    'mt_messaging_cred authorization dlr_level': 'True',
    'mt_messaging_cred authorization hex_content': 'True',
    'mt_messaging_cred authorization http_balance': 'True',
    'mt_messaging_cred authorization http_bulk': 'True',
    'mt_messaging_cred authorization http_dlr_method': 'True',
    'mt_messaging_cred authorization http_long_content': 'True',
    'mt_messaging_cred authorization http_rate': 'True',
    'mt_messaging_cred authorization http_send': 'True',
    'mt_messaging_cred authorization priority': 'True',
    'mt_messaging_cred authorization schedule_delivery_time': 'True',
    'mt_messaging_cred authorization smpps_send': 'True',
    'mt_messaging_cred authorization src_addr': 'True',
    'mt_messaging_cred authorization validity_period': 'True',
    'mt_messaging_cred defaultvalue src_addr': 'None',
    'mt_messaging_cred quota balance': 4000,
    'mt_messaging_cred quota early_percent': 'ND',
    'mt_messaging_cred quota http_throughput': 'ND',
    'mt_messaging_cred quota smpps_throughput': 'ND',
    'mt_messaging_cred quota sms_count': 'ND',
    'mt_messaging_cred valuefilter content': '.*',
    'mt_messaging_cred valuefilter dst_addr': '.*',
    'mt_messaging_cred valuefilter priority': '^[0-3]$',
    'mt_messaging_cred valuefilter src_addr': '^()$',
    'mt_messaging_cred valuefilter validity_period': '^d+$',
    'password': '$PASSWORD',
    'smpps_cred authorization bind': 'True',
    'smpps_cred quota max_bindings': '1',
    'status': true,
    'uid': '$UID',
    'username': '$USERNAME'
}
```
Keep in mind, to not include `mt_messaging_cred quota balance`, and `mt_messaging_cred quota sms_count` keys in your `user` collection if you have `jasmin` internal billing enabled.
Also notice there is an extra key `status`. This key is a special `bool` field. You have to include it in all `user`, `group`, and `smppccm` documents. The package will use the value of this key to `Enable` if `True`, `Disable` if `False` the `user`, and `group`. In case of `smppccm` the package will `start` the `smppccm` if `True` and `stop` it if `False`.

Also keep in mind the package will not copy any files to the `jasmin` instance. all communications are done through `Telnet`. So, in case of `MoInterceptor`, and `MtInterceptor`. You will have to make the script accessible to the `jasmin` server. Example of a `MtInterceptor` document:
```
{
    _id: '$ORDER',
    filters: 'premium_numbers',
    order: '$ORDER',
    script: 'python3(/tmp/premium.py)',
    type: 'StaticMTInterceptor'
}
```
You will have to make the sure `jasmin` have access to `/tmp/premium.py` before adding the document to MongoDB cluster.


### Start the service
#### Set variables
To start the package. you have to export the fallowing variables:
```
JASMIN_CLI_HOST                         =       **REQUIRED:NoDefault**
JASMIN_CLI_PORT                         =               8990
JASMIN_CLI_TIMEOUT                      =                30
JASMIN_CLI_AUTH                         =               True
JASMIN_CLI_USERNAME                     =             jcliadmin
JASMIN_CLI_PASSWORD                     =              jclipwd
JASMIN_CLI_STANDARD_PROMPT              =             "jcli : "
JASMIN_CLI_INTERACTIVE_PROMPT           =               "> "
MONGODB_CONNECTION_STRING               =       **REQUIRED:NoDefault**
MONGODB_MODULES_DATABASE                =       **REQUIRED:NoDefault**
SYNC_CURRENT_FIRST                      =               True
JASMIN_MONGO_CONFIGURATION_LOG_PATH     =             /var/log
```
#### Start Change-Stream
```
jasminmongoconfd
```
