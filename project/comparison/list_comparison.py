# coding: utf8


import os
from collections import namedtuple

from common.logger import log_new

ListDiff = namedtuple('ListDiff', ['correct_list', 'both_missing', 'current_only_missing', 'baseline_only_missing', 'both_present'])
"""
Container with lists of screenshot lists comparison results

:param correct_list: expected names obtained from scenario json
:type list[str]
:param both_missing: names missing in both current and baseline lists
:type list[str]
:param current_missing: names missing only in current list
:type list[str]
:param baseline_missing: names missing only in baseline list
:type list[str]
:param both_present: names present in both datasets
:type list[str]
"""

def compare_lists(current_list, baseline_list, correct_list):
    """
    :param current_list: list of screenshots in current dataset
    :type current_list: list[str]
    :param baseline_list: list of screenshots in baseline dataset
    :type baseline_list: list[str]
    :param correct_list: correct/expected list of screenshots obtained from scenario json parsing
    :type correct_list: list[str]
    :return: container with list comparison results, correct/expected list
    :rtype: ListDiff
    """
    log_new('compare_lists')

    def get_filenames_set(paths_set):
        log_new('get_filenames_set')
        return set([
            os.path.split(path)[1]
            for path in paths_set
        ])

    assert isinstance(current_list, list)
    assert isinstance(baseline_list, list)
    assert isinstance(correct_list, list)

    current_set = get_filenames_set(current_list)
    baseline_set = get_filenames_set(baseline_list)
    all_set = current_set.union(baseline_set)
    
    if correct_list == []:
        correct_set = all_set
    else:
        correct_set = set(correct_list)

    image_list_diff = ListDiff(
        correct_list=list(correct_set),
        both_missing=list(correct_set.difference(all_set)),
        current_only_missing=list(all_set.difference(current_set)),
        baseline_only_missing=list(all_set.difference(baseline_set)),
        both_present=list(current_set.intersection(baseline_set))
    )

    return image_list_diff


def create_process_list(correct_list, lists_diff, current_dir, baseline_dir):
    """
    :param correct_list: correct/expected list of screenshots obtained from scenario json parsing
    :type correct_list: list[str]
    :param lists_diff: container with lists of screenshot lists comparison results
    :type lists_diff: ListDiff
    :param current_dir: path to directory with images from current dataset
    :type current_dir: str
    :param baseline_dir: path to directory with images from baseline dataset
    :type baseline_dir: str
    :return: list of paths pairs including current screenshot and baseline screenshot paths
    :rtype: list[(list[str], list[str])]
    """
    log_new('create_process_list')
    
    process_list = []
    
    for filename in correct_list:
        
        if filename in lists_diff.both_present:
            current_file = os.path.join(current_dir, filename)
            baseline_file = os.path.join(baseline_dir, filename)
            
        elif filename in lists_diff.current_only_missing:
            current_file = None
            baseline_file = os.path.join(baseline_dir, filename)
            
        elif filename in lists_diff.baseline_only_missing:
            current_file = os.path.join(current_dir, filename)
            baseline_file = None
            
        elif filename in lists_diff.both_missing:
            current_file = None
            baseline_file = None
            
        else:
            raise Exception('Filename from correct_list: {} not found in lists_diff'.format(filename))
            
        process_list.append([filename, current_file, baseline_file])
        
    return process_list
