# coding: utf8

"""
NIFFLER
script for artifact links obtaining via TeamCity RestAPI
"""

import argparse
from lxml import etree
import os
import requests
import sys
import zipfile

from common.config_lib import prepare_directory, get_timestamp, delete_directory
from common.configurator import Config
from common.logger import log, log_new, logg, logging


def get_parameters():
    log_new('_get_parameters')

    logg('cl', sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--build-number", type=str, required=True)
    args = parser.parse_args()
    logg('args', args)
    return args


def prepare_dir_structure(config):
    log_new('prepare_dir_structure')
    prepare_directory(config.TEMP_DIR)
    prepare_directory(config.TEMP_ARTIFACTS_DIR)


def get_teamcity_build_info(build_number, build_fields, config):
    log_new('get_teamcity_build_info')

    def get_build_url(build_number, build_fields):
        log_new('get_build_url')
        query_parameters = [
            ['fields', 'build(' + ','.join(build_fields) + ')'],
            ['locator', 'number:' + build_number],
        ]
        path = config.REMOTE_TC_SERVER_URL + '/app/rest/buildTypes/id:' + config.REMOTE_TC_PROJECT + '/builds'
        query = '&'.join(map(lambda pair: pair[0] + '=' + pair[1], query_parameters))
        url = path + '?' + query
        return url

    def parse_response(response, build_fields):
        log_new('parse_response')
        response_content = response.content
        root = etree.fromstring(response_content)
        node = root.xpath('/builds/build')[0]
        result = {}
        for field_name in build_fields:
            value = node.get(field_name)
            logg(field_name, value)
            assert value is not None
            result[field_name] = value
        return result

    url = get_build_url(build_number, build_fields)
    logg('url', url)

    response = requests.get(url, auth=(config.REMOTE_TC_LOGIN, config.REMOTE_TC_PASSWORD))
    logg('Response content', response.content)

    result = parse_response(response, build_fields)

    return result


def get_teamcity_artifact_file_name(build_number, config):
    log_new('get_artifact_file_name')

    artifact_file_name = ''.join((
        config.ARTIFACT_NAME,
        '-',
        build_number,
        config.ARTIFACT_FORMAT
    ))
    logg('artifact_file_name', artifact_file_name)
    return artifact_file_name


def get_teamcity_artifact_url(build_number, artifact_file_name, config):
    log_new('get_artifact_url')

    url = '/'.join((
        config.REMOTE_TC_SERVER_GUEST_URL,
        'repository/download',
        config.REMOTE_TC_PROJECT,
        build_number,
        artifact_file_name
    ))
    logg('url created', url)
    return url


def check_build_status(build_number, config):
    build_info = get_teamcity_build_info(build_number, ['id', 'status'], config)
    build_status = build_info['status']

    if not build_status == 'SUCCESS':
        msg = 'Build status is not SUCCESS, actual status: {} '.format(build_status)
        raise Exception(msg)


def download_teamcity_artifact(artifact_url, artifact_file):
    log_new('download_teamcity_artifact')
    logg('artifact_url', artifact_url)
    logg('artifact_file', artifact_file)

    response = requests.get(artifact_url)
    logg('response', response)
    status_code = response.status_code
    logg('status_code', status_code)
    assert status_code == 200, 'wrong status code: {}'.format(status_code)

    with open(artifact_file, 'wb') as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)


def unzip(archive, path):
    log_new('unzip')
    logg('archive', archive)
    logg('path', path)

    with zipfile.ZipFile(archive, "r") as z:
        z.extractall(path)


def check_artifacts(artifact_path, config):
    log_new('_check_artifacts')

    artifacts = config.ARTIFACTS + config.ARTIFACTS_X86

    artifact_files = os.listdir(artifact_path)
    not_found_files = filter(lambda name: name not in artifact_files, artifacts)
    assert len(not_found_files) is 0, 'Artifact files not found: {}'.format(not_found_files)


# will be moved to commons/config_lib
def remove_files_if(func, files):
    log_new('remove_files_if')
    for file in files:
        if func(file):
            if os.path.isfile(file):
                logg('deleting file', file)
                os.remove(file)
            else:
                delete_directory(file)


def delete_unnecessary_artifacts(artifact_path, config):
    log_new('delete_unnecessary_artifacts')

    artifact_files = map(lambda name: os.path.join(artifact_path, name), os.listdir(artifact_path))

    artifacts = config.ARTIFACTS + config.ARTIFACTS_X86

    @logging
    def delete_condition(name):
        return os.path.split(name)[1] not in artifacts

    remove_files_if(delete_condition, artifact_files)


# will be moved to commons/config_lib
def rename_files(func, files):
    log_new('rename_files')
    for file in files:
        os.rename(file, func(file))


def rename_artifacts(build_number, artifact_path):
    log_new('rename_artifacts')

    @logging
    def add_build_to_filename(filename, extensions):
        for extension in extensions:
            if extension in filename:
                new_filename = '{}_{}{}'.format(filename.replace(extension, ''), build_number, extension)
                log('{} -> {}'.format(filename, new_filename))
                return new_filename

    artifact_files = map(lambda name: os.path.join(artifact_path, name), os.listdir(artifact_path))
    artifact_extensions = ['.2gis', '.apk']   #will be moved to commons/config

    rename_files(lambda name: add_build_to_filename(name, artifact_extensions), artifact_files)


def main():
    log_new('_main')

    parameters = get_parameters()

    config = Config()

    prepare_dir_structure(config)

    build_number = str(parameters.build_number)
    check_build_status(build_number, config)

    artifact_file_name = get_teamcity_artifact_file_name(build_number, config)
    artifact_url = get_teamcity_artifact_url(build_number, artifact_file_name, config)
    artifact_file = os.path.join(config.TEMP_ARTIFACTS_DIR, artifact_file_name)

    download_teamcity_artifact(artifact_url, artifact_file)

    unzip(artifact_file, config.TEMP_ARTIFACTS_DIR)

    check_artifacts(config.TEMP_ARTIFACTS_DIR, config)

    delete_unnecessary_artifacts(config.TEMP_ARTIFACTS_DIR, config)

    rename_artifacts(build_number, config.TEMP_ARTIFACTS_DIR)

    return 0


if __name__ == '__main__':
    log_new('NIFFLER')
    logg('started at', get_timestamp())
    retval = main()
    logg('exit code', retval)
    exit(retval)
    logg('finished at', get_timestamp())
