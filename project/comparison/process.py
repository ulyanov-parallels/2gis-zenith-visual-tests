# coding: utf8


import argparse
import os
import sys

import image_comparison
import list_comparison
import log_comparison
import statistics
import test_data
import webreport_generator

from common.config_lib import copy_directory
from common.config_lib import prepare_directory
from common.config_lib import save_file
from common.configurator import Config
import common.jsoner as jsoner
from common.logger import log_new, logg
from webreport_generator import create_webreport


def get_parameters(config):
    log_new('_get_parameters')

    logg('cl', sys.argv)

    parser = argparse.ArgumentParser()

    parser.add_argument('--current-dir', '-c', type=str, required=True)
    parser.add_argument('--baseline-dir', '-b', type=str, required=True)
    parser.add_argument('--diff-dir', '-d', type=str, required=True)
    parser.add_argument('--rgb-threshold', '-f1', type=int, required=False, default=config.DEFAULT_RGB_THRESHOLD)
    parser.add_argument('--size-threshold', '-f2', type=int, required=False, default=config.DEFAULT_SIZE_THRESHOLD)
    parser.add_argument('--test_name', '-t', type=str, required=False)
    parser.add_argument('--base_name', '-base', type=str, required=True)
    parser.add_argument('--device_name', '-device', type=str, required=True)
    parser.add_argument('--current-build', '-cb', type=int, required=True)
    parser.add_argument('--baseline-build', '-bb', type=int, required=True)
    parser.add_argument('--current-test-build', '-ct', type=int, required=True)
    parser.add_argument('--baseline-test-build', '-bt', type=int, required=True)

    parameters = parser.parse_args()

    logg('parameters', parameters)

    assert isinstance(parameters.rgb_threshold, int)
    assert isinstance(parameters.size_threshold, int)
    assert isinstance(parameters.current_build, int)
    assert isinstance(parameters.baseline_build, int)
    assert isinstance(parameters.current_test_build, int)
    assert isinstance(parameters.baseline_test_build, int)

    return parameters


def prepare_dir_structure(parameters, config):
    log_new('prepare_dir_structure')

    screens_diff_dir = os.path.join(parameters.diff_dir, 'screens')

    prepare_directory(screens_diff_dir)

    prepare_directory(config.TEMP_ARTIFACTS_DIR)

    return screens_diff_dir


def main():
    log_new('_main')

    config = Config()

    parameters = get_parameters(config)

    screens_diff_dir = prepare_dir_structure(parameters, config)

    current_data = test_data.TestData(parameters.current_dir, config.RESULTS_EXTENSIONS)
    baseline_data = test_data.TestData(parameters.baseline_dir, config.RESULTS_EXTENSIONS)

    current_images = current_data.get_files('screens')
    current_images_dir = current_data.get_dir('screens')

    baseline_images = baseline_data.get_files('screens')
    baseline_images_dir = baseline_data.get_dir('screens')

    logg('current_images', current_images)
    logg('baseline_images', baseline_images)

    current_log = current_data.get_files('logs')[0]
    baseline_log = baseline_data.get_files('logs')[0]

    if parameters.test_name is None:    # case of local run
        correct_images = []
    else:
        current_scenario = current_data.get_files('scenario')[0]
        baseline_scenario = baseline_data.get_files('scenario')[0]
        correct_images = jsoner.create_correct_list(current_scenario, baseline_scenario)

    images_lists_diff = list_comparison.compare_lists(current_images, baseline_images, correct_images)

    log_diffs = log_comparison.compare_logs(current_log, baseline_log, correct_images, config)

    images_process_list = list_comparison.create_process_list(
        correct_images, images_lists_diff, current_images_dir, baseline_images_dir)

    images_diffs = image_comparison.compare_images(
        images_process_list, screens_diff_dir, parameters.rgb_threshold, parameters.size_threshold, config)

    stat, status = statistics.create_image_statistics(images_lists_diff, images_diffs)

    webreport = create_webreport(images_diffs, log_diffs, stat, status, parameters, config)

    save_file(os.path.join(config.TEMP_ARTIFACTS_DIR, 'report.html'), webreport)
    copy_directory(config.WEB_REPORT_LIB_DIR, config.TEMP_ARTIFACTS_WEBREPORT_LIB_DIR)
    copy_directory(config.TEMP_DATA_DIR, config.TEMP_ARTIFACTS_DATA_DIR)

    return 0
