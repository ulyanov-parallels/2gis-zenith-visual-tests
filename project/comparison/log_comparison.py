# coding: utf8


import difflib
from collections import namedtuple
import os

from common.config_lib import read_file
from common.logger import log_new, logg


LogSet = namedtuple('LogSet', ['correct', 'current', 'baseline', 'diff'])

"""
Container with log comparison result:

:param correct: name of log part from list of correct/expected names
+ before and after parts (before, testcase 1, ... ,testcase n, after)
:type correct: str
:param current: part of current log (with delta and collapsing markup)
:type current: list[str] | None
:param baseline: part of baseline log (with delta and collapsing markup)
:type baseline: list[str] | None
:param diff: diff b/w corresponding part of current and baseline logs (with delta and collapsing markup)
:type diff: list[str] | None
"""


def get_testcase_name(filename):
    
    """
    from README.md:
    
    SCREENSHOT NAME FORMAT AGREEMENT
    in projects zenith_visual, zenith_visual_tests:
    -----------------------------------
    [testcase id]_[screenshot number in tc]_[feature-test name]_[location name]_[scale]_[angle].png
    
    where:
    [testcase id] - tc id in format: test suite name + sequential number of test case in test suite;
    [screenshot number in tc] -  sequential number in format scr#;
    [feature-test name] - subj;
    [location name] - subj;
    [scale] - scale (z coordinate) value (int);
    [angle] - angle (horizontal) value (int);
    
    example:
    smoke2_scr5_loc-test_Ostankino Tower_25000_0.png
    -----------------------------------
    6 parts "_"-separated and "_" in parts not allowed! Space in parts allowed.

    * * * * * * * * * * * * * * * * * *

    TEST CASE NAME FORMAT AGREEMENT
    in project zenith_visual
    -----------------------------------
    [testcase id]_[feature-test name]_[location name]
    
    where:
    [testcase id] - tc id in format: test suite name + sequential number of test case in test suite;
    [feature-test name] - subj;
    [location name] - subj;
    -----------------------------------
    """
    
    def is_png(name):
        log_new('is_png')
        logg('name', name)
        return name.endswith('.png')

    # assert is_png(filename)
    # disabled due to bug
    # TODO: fix ZNTH-2375
    
    name_parts = os.path.basename(filename).rstrip('.png').split('_')

    
    assert len(
        name_parts) == 6, 'Unexpected screenshot name format: {}, number of "_" divided parts: {} (6 expected)'.format(
        filename, str(len(name_parts)))
    
    testcase_id = name_parts[0]
    feature_test_name = name_parts[2]
    location_name = name_parts[3]
    return '_'.join([testcase_id, feature_test_name, location_name])


def _compartmentalize_log(content):
    log_new('compartmentalize_log')
    
    compartmentalized_content = {}
    part = []
    before_key = True
    after_key = False
    testcase_name = 'undefined'
    
    for i, line in enumerate(content):
        
        if 'make_screenshot(' in line and 'finish.png' not in line:
            testcase_name = get_testcase_name(line)
        
        if 'started test case' in line and 'Executing' in line:
            if before_key:
                compartmentalized_content['before'] = part
                before_key = False
                after_key = False
                part = []
            testcase_name = 'undefined'
            part.append(line)
        
        elif 'ended test case' in line and 'Executing' not in line:
            part.append(line)
            compartmentalized_content[testcase_name] = part
            part = []
            after_key = True
        
        elif i == len(content) - 1:  # last line
            part.append(line)
            if before_key:
                compartmentalized_content['before'] = part
            elif after_key:
                compartmentalized_content['after'] = part
            else:
                compartmentalized_content[testcase_name] = part
        else:
            part.append(line)
    
    return compartmentalized_content


def _insert_markers(diff_content, log_content):
    if diff_content is None:
        return log_content
    
    result = []
    for log_line in log_content:
    
        #TODO: With current approach all duplicated lines in log_content will be marked if at least one of them has diff
        
        found_symbol = False
        for symbol in ['-', '+', '?']:
            log_line_with_symbol = '{} {}'.format(symbol, log_line)
            if log_line_with_symbol in diff_content:
                result.append(log_line_with_symbol)
                found_symbol = True
                break
        if not found_symbol:
            result.append(log_line)
            
    return result


def _insert_collapsing(content, distance):
    result = []
    collapse_info = []
    collapse = False
    count = 0
    
    def _uncollapse_tail(content, distance):
        # todo: need solution for corner-case: when after tail uncollapsing collapsed rows number becomes < distance
        content_length = len(content) - 1
        for j in range(min(distance, content_length)):
            content[content_length - j] = False
        return content
      
    for line in content:
       
        if not collapse:
            count += 1
        else:
            count = 0
        
        if count > distance:
            collapse = True
        
        if line.startswith('+') or line.startswith('-') or line.startswith('?'):
            collapse = False
            collapse_info = _uncollapse_tail(collapse_info, distance)

        collapse_info.append(collapse)
    collapse_info = _uncollapse_tail(collapse_info, distance)
    
    for line, collapse_state in zip(content, collapse_info):
        if collapse_state:
            line = '* {}'.format(line)
        result.append(line)
        
    return result


def remove_timestamps(content):
    new_content = []
    
    years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for line in content:
        
        def find(str):
            return str in line
        
        if not (len(filter(find, years)) == 1 and len(filter(find, week_days)) == 1 and len(filter(find, months)) == 1):
            new_content.append(line)
    
    return new_content
    
    
def compare_logs(current_log, baseline_log, correct_list, config):
    """
    :param current_log: path to current log file
    :type current_log: str
    :param baseline_log: path to baseline log file
    :type baseline_log: str
    :param correct_list: list of correct/expected images (subcases) derived from scenario json
    :type correct_list: list[str]
    :param config: configuration
    :type config: DefaultConfig
    :return container with log data
    :rtype list[LogSet]
    """
    log_new('compare_logs')
    
    assert isinstance(current_log, str)
    assert isinstance(baseline_log, str)
    
    current_content = remove_timestamps(read_file(current_log))
    baseline_content = remove_timestamps(read_file(baseline_log))
    
    current_compartmentalized_log = _compartmentalize_log(current_content)
    baseline_compartmentalized_log = _compartmentalize_log(baseline_content)
    
    correct_log_names = ['before']
    last_name = ''
    for screenshot_name in correct_list:
        tc_name = get_testcase_name(screenshot_name)
        if tc_name != last_name:
            correct_log_names.append(tc_name)
            last_name = tc_name
    
    correct_log_names.append('after')

    result = []
    for name in correct_log_names:

        current_part = current_compartmentalized_log.get(name)
        baseline_part = baseline_compartmentalized_log.get(name)

        if current_part is None or baseline_part is None:
            result.append(LogSet(name, current_part, baseline_part, None))
            continue

        """
        important!
        in difflib comparison order is: baseline - 1st, current - 2nd
        """
        
        diff = list(difflib.ndiff(baseline_part, current_part))

        filtered_diff = [line
                         for line in diff
                         if line.startswith('+') or line.startswith('-') or line.startswith('?')]

        if len(filtered_diff) == 0:
            result.append(LogSet(name, current_part, baseline_part, None))
            continue

        if config.FILTER_DIFF_LOG:
            diff = filtered_diff
        
        current_part = _insert_collapsing(_insert_markers(diff, current_part), config.COLLAPSE_DISTANCE_ROWS)
        baseline_part = _insert_collapsing(_insert_markers(diff, baseline_part), config.COLLAPSE_DISTANCE_ROWS)
        diff = _insert_collapsing(diff, config.COLLAPSE_DISTANCE_ROWS)
        
        result.append(LogSet(name, current_part, baseline_part, diff))
        
    return result
