import logging
import os
import pprint

import getrealty.settings


pp = pprint.PrettyPrinter(width=1)
config = getrealty.settings.config

logger = logging.getLogger(__name__)


class MyDirs(object):

    """Class for creating necessary directories for each rnumber and retrieving
    dirs and files"""

    def __init__(self):

        # print("jason", config['defaults']['WORK_DIR'])
        if config['defaults']['WORK_DIR'] == './':
            self.cache_dir = self._getabspath("/cache")
            self.advanced_search_dir = self._getabspath("/searches")
            self.excel_dir = self._getabspath("/excel")
            self.log_dir = self._getabspath("/cache")
        else:
            self.cache_dir = \
                self._getabspath("/cache/" + config['defaults']['COUNTY'])
            self.advanced_search_dir = \
                self._getabspath("/searches/" + config['defaults']['COUNTY'])
            self.excel_dir = \
                self._getabspath("/excel/" + config['defaults']['COUNTY'])
            self.log_dir = \
                self._getabspath("/cache/" + config['defaults']['COUNTY'])

    def _getabspath(self, local_path):

        default_run_dir = '.'

        path = os.path.abspath(default_run_dir + local_path)
        return(path)

    def buildmydirs(self):

        for dir in (self.cache_dir, self.advanced_search_dir, self.excel_dir):
            print('dir = ', dir)
            try:
                os.makedirs(dir, exist_ok=True)
            except Exception:
                print("Creation of the directory %s failed" % dir)
                exit()

    def cachedir(self):
        return(self.cache_dir)

    def exceldir(self):
        return(self.excel_dir)

    def logdir(self):
        return(self.log_dir)

    def advanced_search_file(self, my_file):
        advanced_search_response_file = self.advanced_search_dir \
            + "/" + config['defaults']['OUTPUT'] + my_file
        return(advanced_search_response_file)

    def prop_id_search_file(self, my_file):
        prop_id_search_response_file = self.advanced_search_dir \
            + "/" + config['defaults']['OUTPUT'] + my_file
        return(prop_id_search_response_file)
