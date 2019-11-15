# coding: utf8


from collections import namedtuple

from common.logger import log_new
from image_comparison import ImageSet   #used by IDE
from log_comparison import LogSet   #used by IDE


Statistics = namedtuple('Statistics', [
    'expected_screens_number',
    'both_missing',
    'current_only_missing',
    'baseline_only_missing',
    'both_present',
    'diffs_created',
    'passed',
    'failed',
    ])
"""
Statistic data
:param expected_screens_number: subj
:type int
:param both_missing: number of screenshots missing in both current and baseline datasets
:type int
:param current_only_missing: number of screenshots missing in only current dataset
:type int
:param baseline_only_missing: number of screenshots missing in only baseline dataset
:type int
:param both_present: number of screenshots present in both datasets
:type int
:param diffs_created: number of diff images created
:type int
:param passed: number of testcases without any difference in result data
:type int
:param failed: number of testcases with found difference(s) in result data
:type int
"""


def create_image_statistics(images_lists_diff, images_diffs):
    """
    :param images_lists_diff: container with image list data
    :type images_lists_diff: ListDiff
    :param images_diffs: container with image data
    :type images_diffs: ImageSet
    :return: container with statistics data
    :rtype: tuple(Statistics, dict[str, str])
    """
    log_new('create_statistics')

    assert isinstance(images_lists_diff, tuple)
    assert isinstance(images_diffs, list)

    def len_nothrow(a):
        return len(a) if a else None

    diff_count = 0
    passed_count = 0
    failed_count = 0
    
    status = {}
    
    for img_set in images_diffs:
        
        name = img_set.correct.rstrip('.png')
        
        if img_set.diff is not None:
            diff_count += 1
            failed_count += 1
            status[name] = 'FAILED'
        else:
            if img_set.current is not None and img_set.baseline is not None:
                passed_count += 1
                status[name] = 'PASSED'
            else:
                failed_count += 1
                status[name] = 'FAILED'
    assert (len(images_diffs) == len(status)), 'Incorrect status dictionary length'
    
    return Statistics(
        len_nothrow(images_lists_diff.correct_list),
        len_nothrow(images_lists_diff.both_missing),
        len_nothrow(images_lists_diff.current_only_missing),
        len_nothrow(images_lists_diff.baseline_only_missing),
        len_nothrow(images_lists_diff.both_present),
        diff_count,
        passed_count,
        failed_count,
    ), status
