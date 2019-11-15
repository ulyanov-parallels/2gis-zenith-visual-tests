# coding: utf8


import argparse
import os
import sys

from common.configurator import Config
from common.logger import log_new, logg


def get_parameters():
    log_new('_get_parameters')

    logg('cl', sys.argv)

    parser = argparse.ArgumentParser()

    parser.add_argument('--current-dir', '-c', type=str, required=True)
    parser.add_argument('--baseline-dir', '-b', type=str, required=True)
    parser.add_argument('--device-name', '-d', type=str, required=True)
    parser.add_argument('--test-name', '-t', type=str, required=True)
    parser.add_argument('--city-name', '-city', type=str, required=True)

    parameters = parser.parse_args()

    logg('parameters', parameters)

    return parameters


def check_input_data(parameters, config):
    log_new('check_input_data')

    def is_existing_dir(path):
        log_new('is_existing_dir')
        return os.path.exists(path) and os.path.isdir(path)

    def check_result_file(cb, result_name):
        log_new('check_result_file')

        def is_existing_file(path):
            log_new('is_existing_file')
            return os.path.exists(path) and os.path.isfile(path)

        if 'current' in cb:
            cb_build = os.path.split(parameters.current_dir)[-1]
            cb_dir = parameters.current_dir
        elif 'baseline' in cb:
            cb_build = os.path.split(parameters.baseline_dir)[-1]
            cb_dir = parameters.baseline_dir

        if result_name == 'scenario':
            result_file_name = '_'.join((
                result_name,
                parameters.test_name,
                parameters.city_name
            )) + config.ARTIFACT_FORMAT
        else:
            result_file_name = '_'.join((
                result_name,
                parameters.device_name,
                parameters.test_name,
                parameters.city_name,
                cb_build
            )) + config.ARTIFACT_FORMAT

        result_file = os.path.join(cb_dir, result_file_name)
        logg('result_file', result_file)

        assert is_existing_file(result_file), 'result file not found: {}'.format(result_file)

    assert is_existing_dir(parameters.current_dir), 'current results directory not found: {}'.format(
        parameters.current_dir)

    assert is_existing_dir(parameters.baseline_dir), 'baseline results directory not found: {}'.format(
        parameters.baseline_dir)

    for cb in ('current', 'baseline'):
        for result_name in config.RESULTS_EXTENSIONS.keys():
            check_result_file(cb, result_name)


def main():
    log_new('_main')

    config = Config()

    parameters = get_parameters()
    check_input_data(parameters, config)

    return 0
