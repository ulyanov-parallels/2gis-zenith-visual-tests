# coding: utf8


import os

from common.config_lib import prepare_directory, unzip, get_files_by_ext, delete_directory
from common.logger import log_new, logg


class TestData:
    """
    Entity working with visual test results
    """
    __slots__ = ('_path', '_extensions')
    
    def __init__(self, path, extensions):
        """
        :param path: path to zip archive with test data
        :type path: str
        :param extensions: list of pairs (filename without extension, extension)
        :type extensions: list[(str, str)]
        """

        log_new('TestData')
        logg('path', path)
        logg('extensions', extensions)
        
        self._path = path
        self._extensions = extensions
        
        zip_files = get_files_by_ext(path, '.zip')

        for zip_file in zip_files:
            for result_name in extensions.keys():
                if result_name in zip_file:
                    dest = os.path.join(path, result_name)
                    prepare_directory(dest)
                    unzip(zip_file, dest)

    def __del__(self):
        delete_directory(self._path)
      
    def get_files(self, result_name):
        results_path = os.path.join(self._path, result_name)
        return get_files_by_ext(results_path, self._extensions[result_name])
    
    def get_dir(self, result_name):
        return os.path.join(self._path, result_name)
