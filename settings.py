import os
import yaml

hash_global = {
    'cache':{},
    'db':{},
    'propValues':{},
    'DBWriteValues':{},
    'rnums':{}
}

# 'cache':         rnumbers in cache?  1 or 0
# 'db':            rnumbers in db?  1 or 0
# 'propValues':    assessed value of properties
# 'DBWriteValues': property data and calcs to be written to DB
# 'rnums':         contains key value pairs for each rnumber.  key is 'omit' value is 1 or 0

cwd = os.getcwd()
config_file = cwd + '/config.yaml'
stream = open(config_file,'r')
config = yaml.safe_load(stream)

def init():
    # make these variables global so that they don't have to be passed to all
    # functions and function calls.
    global hash_global
    global config

