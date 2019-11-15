# coding: utf8


import json

from common.config_lib import save_file, read_file
from common.logger import log_new, logg


def _check_jsons_identity(json1, json2):
    log_new('_check_jsons_identity')
    
    content1 = read_file(json1)
    content2 = read_file(json2)
    
    assert len(content1) == len(content2), 'Different lengths of scenario jsons: {} rows vs {} rows'.format(len(content1), len(content2))
    
    for line1, line2 in zip(content1, content2):
        if '_datasource_layout' not in line1 and '_datasource_layout' not in line2:
            assert line1 == line2, 'Different content of scenario jsons, line1: {} vs line2: {}'.format(line1, line2)


def add_build_number_to_base_in_scenario(path, build_number):
    """
    :param path: path to scenario json file
    :type path: str
    :param build_number: number of build
    :type build_number: int
    """
    log_new('add_build_number_to_base_in_scenario')
    logg('path', path)
    logg('build_number', build_number)
    content = read_file(path)
    new_content = []
    found_key = False
    for line in content:
        if '_datasource_layout' in line and '.2gis' in line:
            new_line = line.replace('.2gis', '_{}.2gis'.format(str(build_number)))
            found_key = True
        else:
            new_line = line
        new_content.append(new_line)
    assert found_key is True, 'Base load not found in scenario'
    save_file(path, new_content)
  

def create_correct_list(scenario1, scenario2):
    """
    :param scenario: path to scenario json file
    :type scenario: str
    :return: list of expected screenshots obtained from json
    :rtype: list[str]
    """
    log_new('create_correct_list')
    logg('scenario1', scenario1)
    logg('scenario2', scenario2)
    
    _check_jsons_identity(scenario1, scenario2)
    
    screenshots = []
    with open(scenario1, 'r') as json_file:
        json_data = json.load(json_file)
    for json_line in json_data:
        if json_line['name'] == 'make_screenshot':
            screenshot_name = json_line['arguments']['file_name'].replace('screens/', '')
            if screenshot_name != 'finish.png':
                screenshots.append(screenshot_name)
    return screenshots
