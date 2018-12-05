import logging
import os
import pprint

import lib.settings


pp = pprint.PrettyPrinter(width=1)
config = lib.settings.config

logger = logging.getLogger(__name__)

class MyDirs(object):

    """Docstring for MyClass. """

    def __init__(self):

        DEFAULT_RUN_DIR = '.'

        # print("jason", config['defaults']['WORK_DIR'])
        if config['defaults']['WORK_DIR'] == './':
            self.CACHE_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/cache")
            self.ADVANCED_SEARCH_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/searches")
            self.EXCEL_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/excel")
            self.LOG_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/cache")
        else :
            self.CACHE_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/cache/" + config['defaults']['COUNTY'])
            self.ADVANCED_SEARCH_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/searches/" + config['defaults']['COUNTY'])
            self.EXCEL_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/excel/" + config['defaults']['COUNTY'])
            self.LOG_DIR = os.path.abspath(DEFAULT_RUN_DIR + "/cache/" + config['defaults']['COUNTY'])


        # if config.DATE or (args.rnumbers and args.rnumbers is "ALL"):
        #     config.DEFAULT_OUPUT = "."

    def buildmydirs(self):

        for dir in (self.CACHE_DIR, self.ADVANCED_SEARCH_DIR, self.EXCEL_DIR):
            print('dir = ', dir)
            try:
                os.makedirs(dir, exist_ok=True)
            except Exception:
                print("Creation of the directory %s failed" % dir)
                exit()

    def cachedir(self):
        # print(self.CACHE_DIR)
        return(self.CACHE_DIR)

    def exceldir(self):
        # print(self.EXCEL_DIR)
        return(self.EXCEL_DIR)

    def logdir(self):
        # print(self.LOG_DIR)
        return(self.LOG_DIR)

    def advanced_search_file(self, my_file):
        # print(self.ADVANCED_SEARCH_DIR)
        ADVANCED_SEARCH_RESPONSE_FILE = self.ADVANCED_SEARCH_DIR + "/" + config['defaults']['OUTPUT'] + my_file
        return(ADVANCED_SEARCH_RESPONSE_FILE)

    def prop_id_search_file(self, my_file):
        # print(self.ADVANCED_SEARCH_DIR)
        PROP_ID_SEARCH_RESPONSE_FILE = self.ADVANCED_SEARCH_DIR + "/" + config['defaults']['OUTPUT'] + my_file
        return(PROP_ID_SEARCH_RESPONSE_FILE)
