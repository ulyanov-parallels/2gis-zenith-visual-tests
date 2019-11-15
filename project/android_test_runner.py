# coding: utf8

"""
ANDROID TEST RUNNER
"""

import argparse
from collections import namedtuple
import os
import sys

from adb_scripts.restart import adb_restart
from adb_scripts.load_base import adb_load_base
from adb_scripts.run_android_test import adb_run_android_test
from common import jsoner
from common.config_lib import get_timestamp, prepare_directory
from common.configurator import Config
from common.logger import log, log_new, logg, logging


Data = namedtuple(
    'Data',
    [
        'base',
        'app_src',
        'scenario_name',
        'scenario_src',
        'sh_script_src',
        'wait_script_src',
        'result_screens_dir',
        'result_logs_dir',
        'device_config_src',
        'device_config_name',
        'log_name',
        'dynamic_layout',
    ])
"""
Container with test data information
:param base: path to base
:type str
:param app_src: path to teastapp apk
:type str
:param scenario_name: name of scenario json in format [testname].json
:type str
:param scenario_src: path to scenario json
:type str
:param sh_script_src: path to android side run shell script
:type str
:param wait_script_src: path to wait.py script
:type str
:param result_screens_dir: path to screenhots destination folder
:type str
:param result_logs_dir: path to logs destination folder
:type str
:param device_config_src: path to device config file
:type str
:param device_config_name: name of device config file in format [device name].config
:type str
:param log_name: (custom) testapp log name
:type str
:param dynamic_layout: path to dynamic_layout (dir)
:type str
"""


def get_parameters():
    log_new('_get_parameters')

    logg('cl', sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--build-number", type=str, required=True)
    parser.add_argument("-d", "--device-name", type=str, required=True)
    parser.add_argument("-t", "--test-name", type=str, required=True)
    parameters = parser.parse_args()
    logg('parameters', parameters)
    return parameters


def prepare_dir_structure(config):
    log_new('prepare_dir_structure')
    prepare_directory(config.TEMP_ARTIFACTS_DIR)


@logging
def add_build_to_filename(filename, extensions, build_number):
    for extension in extensions:
        if filename[-len(extension):] == extension:
            new_filename = '{}_{}{}'.format(filename[:-len(extension)], build_number, extension)
            log('{} -> {}'.format(filename, new_filename))
            return new_filename


def select_artifact(device, config):
    if config.DEVICE_PLATFORMS[device] == 'arm':
        return config.ARTIFACTS
    elif config.DEVICE_PLATFORMS[device] == 'x86':
        return config.ARTIFACTS_X86
    else:
        raise Exception('Incorrct device platform: {}'.format(str(config.DEVICE_PLATFORMS[device])))


def check_input_artifacts(artifacts_path, build_number, device, config):
    log_new('check_input_artifacts')
    logg('artifacts_path', artifacts_path)

    artifacts = select_artifact(device, config)
    artifact_files = os.listdir(artifacts_path)
    expected_artifact_files = map(lambda name: add_build_to_filename(name, config.ARTIFACT_EXTENSIONS, build_number),
                                  artifacts)
    logg('expected_artifact_files', expected_artifact_files)
    not_found_files = filter(lambda name: name not in artifact_files, expected_artifact_files)
    assert len(not_found_files) is 0, 'Artifact files not found: {}'.format(not_found_files)


def get_test_data(parameters, config):
    log_new('prepare_test_data')

    artifacts = select_artifact(parameters.device_name, config)
    build_base = add_build_to_filename(artifacts.base, config.ARTIFACT_EXTENSIONS, parameters.build_number)
    build_dynamic_layout = add_build_to_filename(
        artifacts.dynamic_layout, config.ARTIFACT_EXTENSIONS, parameters.build_number)
    build_app = add_build_to_filename(artifacts.app, config.ARTIFACT_EXTENSIONS, parameters.build_number)
    scenario_name = '.'.join((parameters.test_name, 'json'))
    device_config_name = config.DEFAULT_DEVICE_CONFIG.replace('device', str(parameters.device_name))

    test_data = Data(
        base=os.path.join(config.TEMP_DATA_DIR, build_base),
        app_src=os.path.join(config.TEMP_DATA_DIR, build_app),
        scenario_name=scenario_name,
        scenario_src=os.path.join(config.ENV_TESTS_DIR, scenario_name),
        sh_script_src=os.path.join(config.ENV_SHELL_SCRIPTS_DIR, config.ANDROID_SIDE_RUN_SCRIPT_NAME),
        wait_script_src=os.path.join(config.ENV_PROJECT_DIR, config.WAIT_SCRIPT_NAME),
        result_screens_dir=os.path.join(config.TEMP_ARTIFACTS_DIR, 'screens'),
        result_logs_dir=os.path.join(config.TEMP_ARTIFACTS_DIR, 'logs'),
        device_config_src=os.path.join(config.ENV_CONFIG_DIR, device_config_name),
        device_config_name=device_config_name,
        log_name=config.LOG_NAME.replace('build', str(parameters.build_number)),
        dynamic_layout=os.path.join(config.TEMP_DATA_DIR, build_dynamic_layout),
    )

    logg('test_data', test_data)

    return test_data


def restart(config):
    log_new('restart')

    adb_restart(config)


def load_base(load_base_parameters, config):
    log_new('load_base')

    adb_load_base(config, load_base_parameters)


def run_android_test(run_android_test_parameters, config):
    log_new('run_android_test')

    adb_run_android_test(config, run_android_test_parameters)


def main():
    log_new('_main')

    parameters = get_parameters()

    config = Config()

    prepare_dir_structure(config)

    check_input_artifacts(config.TEMP_DATA_DIR, parameters.build_number, parameters.device_name, config)

    test_data = get_test_data(parameters, config)

    config.define_android_paths(test_data.base)

    jsoner.add_build_number_to_base_in_scenario(test_data.scenario_src, parameters.build_number)

    restart(config)

    load_base([
        test_data.base,
        parameters.device_name,
    ], config)

    run_android_test([
        parameters.device_name,
        test_data.result_screens_dir,
        test_data.result_logs_dir,
        test_data.app_src,
        test_data.scenario_name,
        test_data.scenario_src,
        test_data.sh_script_src,
        test_data.device_config_src,
        test_data.device_config_name,
        test_data.log_name,
        test_data.dynamic_layout,
    ], config)

    return 0


if __name__ == '__main__':
    log_new('ANDROID TEST RUNNER')
    logg('started at', get_timestamp())
    retval = main()
    logg('exit code', retval)
    logg('finished at', get_timestamp())
    sys.exit(retval)
