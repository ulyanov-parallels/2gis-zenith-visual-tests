# coding: utf8

"""
QA Robot
"""

import argparse
import sys

from common.config_lib import get_timestamp
from common.configurator import Config
from common.logger import log_new, logg, log
from teamcity_client import TCServerInfo, add_comment, add_tags, get_builds, start_build, _wait_builds


def _get_parameters():
    log_new('_get_parameters')

    logg('cl', sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("--current-results-build", type=str, required=False)     #left for backward compatability
    parser.add_argument("--baseline-results-build", type=str, required=False)    #left for backward compatability
    parser.add_argument("--current-build", type=str, required=True)
    parser.add_argument("--baseline-build", type=str, required=True)
    parser.add_argument("--base-name", type=str, required=True)
    parser.add_argument("--test-name", type=str, required=True)
    parser.add_argument("--devices", type=str, required=True)
    parser.add_argument("--rgb-filter-threshold", type=str, required=True)
    parser.add_argument("--size-filter-threshold", type=str, required=True)
    parser.add_argument("--test-branch", type=str, required=True)
    parser.add_argument("--recreate-artifacts", type=str, default="false", required=True)
    parser.add_argument("--qa-tcserver", type=str, required=True)

    parameters = parser.parse_args()
    logg('parameters', parameters)
    return parameters


def _create_queue(builds_info, config):
    log_new('_create_queue')

    tagged_for_execution = []
    ready_for_execution = []
    processed_tags = [config.tag_finished, config.tag_progress, config.tag_broken, config.tag_baseline]
    processed_tags_set = set(processed_tags)

    for build_number, build_info in builds_info.iteritems():

        if not build_info.status == 'SUCCESS':
            continue

        is_tagged = len(build_info.tags) > 0
        is_root = config.tag_root in build_info.tags
        is_processed = len(set(build_info.tags) & processed_tags_set) > 0

        if is_root:
            logg('tagged for execution', build_number)
            tagged_for_execution.append(int(build_number))
        elif not is_processed:
            if is_tagged:
                logg('tagged with irrelevant tag(s) ready for execution', build_number)
            else:
                logg('untagged ready for execution', build_number)
            ready_for_execution.append(int(build_number))

    queue = tagged_for_execution + ready_for_execution

    logg('unsorted queue', queue)

    queue.sort(reverse=True)

    logg('sorted queue', queue)

    if len(queue) == 0:
        raise Exception('No builds in queue')

    return queue


def _set_tag(chosen_build, builds_info, del_tags, new_tag, tcserver_info):
    log_new('_set_tag')
    log('{} -> {}'.format(del_tags, new_tag))

    build_info = builds_info[chosen_build]
    old_tags = set(build_info.tags)
    logg('old_tags', old_tags)
    tags_to_delete = set(del_tags)
    new_tags = (old_tags - tags_to_delete) | {new_tag}

    add_tags(chosen_build, new_tags, tcserver_info)


def _set_progress_tag(chosen_build, builds_info, config, tcserver_info):
    log_new('_set_progress_tag')

    _set_tag(chosen_build, builds_info, [config.tag_root, config.tag_broken, config.tag_finished],
             config.tag_progress, tcserver_info)


def _set_finished_tag(chosen_build, builds_info, config, tcserver_info):
    log_new('_set_finished_tag')

    _set_tag(chosen_build, builds_info, [config.tag_progress], config.tag_finished, tcserver_info)


def _set_broken_tag(chosen_build, builds_info, config, tcserver_info):
    log_new('_set_broken_tag')

    _set_tag(chosen_build, builds_info, [config.tag_progress], config.tag_broken, tcserver_info)


def _choose_build(config, tcserver_info):
    log_new('_choose_build')

    builds_info = get_builds(tcserver_info)
    queue = _create_queue(builds_info, config)

    chosen_build = str(queue[0])
    log_new('* * * * * * *')
    logg('chosen_build', chosen_build)
    log('* * * * * * *')

    return chosen_build.strip('"')


def _find_tagged_baseline_build(config, tcserver_info):
    log_new('_find_tagged_baseline_build')

    builds_info = get_builds(tcserver_info)

    tagged = []

    for build_number, build_info in builds_info.iteritems():
        if config.tag_baseline in build_info.tags:
            tagged.append(int(build_number))

    logg('tagged baseline build', tagged)

    return str(max(tagged)) if len(tagged) > 0 else None


def _initialize_build(build_number, config, tcserver_info):
    log_new('_initialize_build')

    builds_info = get_builds(tcserver_info, build_number)
    _set_progress_tag(build_number, builds_info, config, tcserver_info)


def _finalize_build(build_number, is_qa_success, config, tcserver_info):
    log_new('_finalize_build')

    assert (build_number is not None)

    builds_info = get_builds(tcserver_info, build_number)

    if is_qa_success:
        _set_finished_tag(build_number, builds_info, config, tcserver_info)
    else:
        _set_broken_tag(build_number, builds_info, config, tcserver_info)


def _check_build_existence(build_number, tcserver_info):
    log_new('_check_build_existence')

    builds_info = get_builds(tcserver_info, build_number)

    if not builds_info: #True if dict is empty
        raise Exception('Build #{} not found with scope depth {}'.format(build_number, tcserver_info.scope))
    else:
        log('Build #{} exists'.format(build_number))


def _check_artifacts(test_name, base_name, device_name, build_number, build_artifacts):
    log_new('_check_artifacts')

    logg('build_number', build_number)
    logg('build_artifacts', build_artifacts)

    correct_artifacts = [
        'logs_{}_{}_{}_{}.zip'.format(device_name.lower(), test_name, base_name, build_number),
        'screens_{}_{}_{}_{}.zip'.format(device_name.lower(), test_name, base_name, build_number),
        'scenario_{}_{}.zip'.format(test_name, base_name),
    ]

    result = True
    for artifact in correct_artifacts:
        if artifact not in build_artifacts:
            result = False
            log('artifact not found {}'.format(artifact))
    return result


def _find_existing_artifacts(chosen_build, test_name, base_name, device_name, tcserver_info):
    log_new('_find_existing_artifacts')

    builds_info = get_builds(tcserver_info)

    found_builds = []

    for build_number, build_info in builds_info.iteritems():
        build_artifacts = build_info.artifacts

        if build_number == chosen_build:
            log(build_number)
            log(build_artifacts)

        if _check_artifacts(test_name, base_name, device_name, chosen_build, build_artifacts):
            found_builds.append(int(build_number))

    result = sorted(found_builds, reverse=True)

    logg('result', result)

    return str(max(result)) if len(result) > 0 else None


def _create_comment(device_name, test_name, base_name, builds):
    return '{}, {}, {}, {}'.format(device_name, test_name, base_name, builds)


def _set_comment(build_number, comment, tcserver_info):
    log_new('_set_comment')

    builds_info = get_builds(tcserver_info, build_number)
    build_info = builds_info[build_number]
    old_comment = build_info.comment
    build_id = build_info.id
    new_comment = '{}\n{}'.format(old_comment, comment)
    add_comment(build_id, new_comment, tcserver_info)


def _run_build(config, qa_tcserver_info, qa_tc_project1_parameters_current, test_branch, qa_comment,
               remote_build_number):
    log_new('_run_build')
    build_id = start_build(qa_tcserver_info, qa_tc_project1_parameters_current, test_branch, qa_comment)
    if build_id is None:
        _finalize_build(remote_build_number, False, config, qa_tcserver_info)

        raise Exception('Build not started!')
    return build_id


def _run_robotic_visual(device_name, test_name, base_name, test_branch, config, build_number, qa_tcserver_info, wait_ids,
                        wait_comments):
    log_new('_run_robotic_visual')

    qa_tc_project1_parameters_current = {
        'device_name': device_name,
        'reverse.dep.*.base_name': base_name,
        'reverse.dep.*.build_number': build_number,
        'reverse.dep.*.test_name': test_name,
    }
    qa_comment = _create_comment(device_name, test_name, base_name, build_number)
    results_build_id = _run_build(
        config, qa_tcserver_info, qa_tc_project1_parameters_current, test_branch, qa_comment, build_number)
    wait_ids.append(results_build_id)
    wait_comments.append(qa_comment)

    return results_build_id


def _run_results_comparison(device_name, parameters, config, current_build_number, baseline_build_number,
                            current_results_build_number, baseline_results_build_number, qa_tcserver_info2):
    log_new('_run_results_comparison')

    base_name = parameters.base_name
    test_name = parameters.test_name
    rgb_threshold = str(parameters.rgb_filter_threshold)
    size_threshold = str(parameters.size_filter_threshold)
    test_branch = parameters.test_branch

    qa_tc_project2_parameters = {
        '01_current_results_build': current_results_build_number,
        '02_baseline_results_build': baseline_results_build_number,
        '03_current_build_number': current_build_number,
        '04_baseline_build_number': baseline_build_number,
        '05_device_name': device_name,
        '06_test_name': test_name,
        '07_base_name': base_name,
        '08_rgb_threshold': rgb_threshold,
        '09_size_threshold': size_threshold,
    }
    qa_comment = _create_comment(device_name, test_name, base_name, '{} vs {}'.format(
        current_build_number, baseline_build_number))

    comparison_build_id = _run_build(
        config, qa_tcserver_info2, qa_tc_project2_parameters, test_branch, qa_comment, None)

    build_numbers = _wait_builds(config, qa_tcserver_info2, [comparison_build_id], [qa_comment])
    return build_numbers[comparison_build_id]


def _run_pipeline(device_name, baseline_build_number, current_build_number, parameters, config, qa_tcserver_info,
                  qa_tcserver_info2, remote_tcserver_info):
    log_new('_run_pipeline')
    logg('on device', device_name)

    base_name = parameters.base_name
    test_name = parameters.test_name

    test_branch = str(parameters.test_branch)

    # todo: when semaphore is ready move outside of devices cycle
    wait_ids = []
    wait_comments = []
    current_results_build_id = None
    baseline_results_build_id = None

    logg('parameters.recreate_artifacts', parameters.recreate_artifacts)

    if not parameters.recreate_artifacts == 'true':
        current_results_build_number = _find_existing_artifacts(
            current_build_number, test_name, base_name, device_name, qa_tcserver_info)

        baseline_results_build_number = _find_existing_artifacts(
            baseline_build_number, test_name, base_name, device_name, qa_tcserver_info)
    else:
        current_results_build_number = None
        baseline_results_build_number = None

    logg('current_results_build_number', current_results_build_number)
    logg('baseline_results_build_number', baseline_results_build_number)

    # run Robotic_Visual (current)
    if current_results_build_number is None:
        current_results_build_id = _run_robotic_visual(
            device_name, test_name, base_name, test_branch, config, current_build_number, qa_tcserver_info, wait_ids,
            wait_comments)

    # run Robotic_Visual (baseline)
    if baseline_results_build_number is None:
        baseline_results_build_id = _run_robotic_visual(
            device_name, test_name, base_name, test_branch, config, baseline_build_number, qa_tcserver_info, wait_ids,
            wait_comments)

    build_numbers = _wait_builds(config, qa_tcserver_info, wait_ids, wait_comments)

    logg('build_numbers after wait', build_numbers)
    logg('current_results_build_id', current_results_build_id)
    logg('baseline_results_build_id', baseline_results_build_id)

    if current_results_build_number is None:
        current_results_build_number = build_numbers[current_results_build_id]
        logg('current_results_build_number', current_results_build_number)
        remote_comment = _create_comment(device_name, test_name, base_name, current_results_build_number)
        _set_comment(current_build_number, remote_comment, remote_tcserver_info)

    if baseline_results_build_number is None:
        baseline_results_build_number = build_numbers[baseline_results_build_id]
        logg('baseline_results_build_number', baseline_results_build_number)
        remote_comment = _create_comment(device_name, test_name, base_name, baseline_results_build_number)
        _set_comment(baseline_build_number, remote_comment, remote_tcserver_info)

    # run Results_Comparison
    comparison_build_number = _run_results_comparison(
        device_name, parameters, config, current_build_number, baseline_build_number, current_results_build_number,
        baseline_results_build_number, qa_tcserver_info2)
    logg('comparison_build_number', comparison_build_number)


def _main():
    log_new('_main')

    parameters = _get_parameters()

    config = Config(parameters.test_name, parameters.qa_tcserver)

    remote_tcserver_info = TCServerInfo(
        config.REMOTE_TC_LOGIN,
        config.REMOTE_TC_PASSWORD,
        config.REMOTE_TC_SERVER_URL,
        config.REMOTE_TC_PROJECT,
        config.REMOTE_TC_SCOPE_DEPTH,
    )

    qa_tcserver_info = TCServerInfo(
        config.QA_TC_LOGIN,
        config.QA_TC_PASSWORD,
        config.qa_tcserver_url,
        config.QA_TC_PROJECT1,
        config.QA_TC_SCOPE_DEPTH,
    )

    qa_tcserver_info2 = TCServerInfo(
        config.QA_TC_LOGIN,
        config.QA_TC_PASSWORD,
        config.qa_tcserver_url,
        config.QA_TC_PROJECT2,
        config.QA_TC_SCOPE_DEPTH,
    )

    baseline_build_number = parameters.baseline_build
    current_build_number = parameters.current_build
    devices = parameters.devices.split(',')

    if '*' in baseline_build_number:
        baseline_build_number = _find_tagged_baseline_build(config, remote_tcserver_info)
        if baseline_build_number is None:
            baseline_build_number = _choose_build(config, remote_tcserver_info)
    else:
        _check_build_existence(baseline_build_number, remote_tcserver_info)
    _initialize_build(baseline_build_number, config, remote_tcserver_info)

    if '*' in current_build_number:
        current_build_number = _choose_build(config, remote_tcserver_info)
    else:
        _check_build_existence(current_build_number, remote_tcserver_info)
    _initialize_build(current_build_number, config, remote_tcserver_info)

    logg('devices', devices)

    for device_name in devices:
        _run_pipeline(device_name, baseline_build_number, current_build_number, parameters, config, qa_tcserver_info,
                      qa_tcserver_info2, remote_tcserver_info)

    _finalize_build(current_build_number, True, config, remote_tcserver_info)
    _finalize_build(baseline_build_number, True, config, remote_tcserver_info)

    return 0


if __name__ == '__main__':
    log_new('QA Robot')
    logg('started at', get_timestamp())
    retval = _main()
    logg('exit code', retval)
    exit(retval)
    logg('finished at', get_timestamp())
