# coding: utf8

import datetime
import os
import shutil
import time
import zipfile

from collections import namedtuple
from logger import *


Artifacts = namedtuple('Artifacts', 'base dynamic_layout app')
"""
Names of expected files in external artifact

:param base: base file name
:type str
:param dynamic_layout: dynamic layout file name
:type str
:param base: base file name
:type str
:param testapp apk file name
:type: str
"""


def get_timestamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%y.%m.%d %H:%M:%S')
    return str(st)


def create_directory(path):
    logg('create_directory', path)
    if not os.path.exists(path):
        log('directory {} not found'.format(str(path)))
        try:
            os.makedirs(path)
        except OSError as e:
            log_new(e)
        else:
            log('directory {} is created'.format(str(path)))


def delete_directory(path):
    """
    CLOSE FILES AND FOLDERS BEFORE DELETION!!!
    """
    logg('delete_directory', path)

    if not os.path.exists(path):
        log('path not found')
    else:
        try:
            shutil.rmtree(path)
        finally:
            if os.path.exists(path):
                log('directory {} deletion failed'.format(str(path)))
            else:
                log('directory {} deleted successfully'.format(str(path)))


def delete_file(path):
    logg('delete_file', path)
    if not os.path.exists(path):
        log('file not found')
    else:
        os.remove(path)


def prepare_directory(path):
    logg('prepare_directory', path)
    delete_directory(path)
    create_directory(path)


def save_file(path, content):
    logg('save_file', path)

    divided_content = []
    for line in content:
        divided_content.append(line)

    try:
        with open(path, "w") as outfile:
            outfile.writelines(divided_content)
    finally:
        if not os.path.exists(path):
            log('File is not saved: {}'.format(path))


def unzip(archive, path):
    log_new('unzip')
    logg('archive', archive)
    logg('path', path)

    with zipfile.ZipFile(archive, "r") as z:
        z.extractall(path)


def get_files_by_ext(path, ext):
    log_new('get_files_by_ext')
    logg('path', path)
    logg('ext', ext)

    files = []
    for file in os.listdir(path):
        if str(file).endswith(ext):
            files.append(os.path.join(path, file))

    logg('files', files)
    return files


def get_files_in_dir(path):
    log_new('get_files_in_dir')
    logg('path', path)

    files = []
    for item in os.listdir(path):
        if os.path.isfile(item):
            files.append(os.path.join(path, item))

    logg('files', files)
    return files


def read_file(path):
    log_new('read_file')
    logg('path', path)
    if os.path.exists(path) is False:
        raise Exception('File not found: ', str(path))
    else:
        with open(path, 'r') as fl:
            content = fl.readlines()
    return content


def copy_directory(path, dest):
    log_new('copy_directory')
    logg('from', path)
    logg('to', dest)
    shutil.copytree(path, dest)
