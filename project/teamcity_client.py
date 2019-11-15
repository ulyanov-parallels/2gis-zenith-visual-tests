# coding: utf8

"""
TeamCity Client

functions for interaction with TeamCity via RestAPI
"""

from collections import namedtuple
from lxml import etree
import requests
import time
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr

from common.logger import log_new, logg, log


TCServerInfo = namedtuple(
    'TCServerInfo',
    [
        'login',
        'password',
        'url',
        'project',
        'scope',
    ])


BuildInfo = namedtuple(
    'BuildInfo',
    [
        'id',
        'number',
        'branch',
        'status',
        'tags',
        'artifacts',
        'comment',
    ])


def add_comment(build_id, comment, tcserver_info):
    log_new('add_comment')

    headers = {'Content-Type': 'text/plain'}

    url = '{}/app/rest/builds/buildType:{},id:{}/comment/'. \
        format(tcserver_info.url, tcserver_info.project, build_id)

    response = requests.put(url, data=comment, headers=headers, auth=(tcserver_info.login, tcserver_info.password))
    log(response.content)


def add_tags(build_number, tags, tcserver_info):
    log_new('add_tags')
    logg('tags', tags)

    tags_count = len(tags)
    tag_names_xml = ''

    for tag in tags:
        tag_names_xml += '<tag name="{}"/>'.format(tag)

    tags_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><tags count="{}">{}</tags>'. \
        format(tags_count, tag_names_xml)
    logg('tags_xml', tags_xml)

    headers = {'Content-Type': 'application/xml'}
    url = '{}/app/rest/builds/buildType:{},number:{}/tags/'. \
        format(tcserver_info.url, tcserver_info.project, build_number)

    response = requests.put(url, data=tags_xml, headers=headers, auth=(tcserver_info.login, tcserver_info.password))
    log(response.content)


def create_tag(tcserver_info, build_id, tag):
    log_new('create_tag')
    logg('tag', tag)

    build_id = str(build_id)

    tags_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><tags count="1"><tag name="{}"/></tags>'. \
        format(tag.lower())
    logg('tags_xml', tags_xml)

    headers = {'Content-Type': 'application/xml'}
    url = '{}/app/rest/builds/buildType:{},id:{}/tags/'.format(tcserver_info.url, tcserver_info.project, str(build_id))

    response = requests.put(url, data=tags_xml, headers=headers, auth=(tcserver_info.login, tcserver_info.password))
    log(response.content)


def ensure_not_single_element_list(li):
    if len(li) == 0:
        return None
    elif len(li) == 1:
        return li[0]
    else:
        return li


def parse_xml_answer(answer, xpath_pattern):
    log_new('parse_xml_answer')

    doc = etree.fromstring(answer.strip())

    result = []

    for element in doc:
        el = etree.fromstring(etree.tostring(element))
        name = ensure_not_single_element_list(el.xpath(xpath_pattern))
        logg('name', name)
        result.append(name.lower())

    return result


def get_artifacts(tcserver_info, build_id):
    log_new('get_artifacts')

    url = ''.join((
        tcserver_info.url,
        '/app/rest/builds/buildType:',
        tcserver_info.project,
        ',id:',
        build_id,
        '/artifacts/children/',
    ))

    logg('url', url)

    response = requests.get(url, auth=(tcserver_info.login, tcserver_info.password))
    answer = response.content
    logg('answer', answer)

    if response.status_code != 200:
        raise Exception(
            'Unable to get builds information from server, status code: {}'.format(str(response.status_code)))

    artifacts = parse_xml_answer(answer, "//file/@name")

    logg('artifacts', artifacts)

    return artifacts


def get_tags(tcserver_info, build_id):
    log_new('get_tags')

    url = ''.join((
        tcserver_info.url,
        '/app/rest/builds/buildType:',
        tcserver_info.project,
        ',id:',
        build_id,
        '/tags/',
    ))

    logg('url', url)

    response = requests.get(url, auth=(tcserver_info.login, tcserver_info.password))
    answer = response.content
    logg('answer', answer)

    if response.status_code != 200:
        raise Exception(
            'Unable to get builds information from server, status code: {}'.format(str(response.status_code)))

    tags = parse_xml_answer(answer, "//tag/@name")

    return tags


def get_builds(tcserver_info, build_number=None):
    log_new('get_builds')

    if build_number is None:
        locator = ''.join((
            '/builds/?locator=count:',
            str(tcserver_info.scope),
            ',branch:default:any,status:SUCCESS',
            '&fields=build(number,id,branchName,status,tags,comment)'
        ))
    else:
        locator = ''.join((
            '/builds/?locator=number:',
            build_number,
            '&fields=build(number,id,branchName,status,tags,comment)'
        ))

    url = ''.join((
        tcserver_info.url,
        '/app/rest/buildTypes/id:',
        tcserver_info.project,
        locator
    ))

    log(url)

    response = requests.get(url, auth=(tcserver_info.login, tcserver_info.password))
    answer = response.content

    log_new('answer:')
    log(answer)

    if response.status_code != 200:
        raise Exception(
            'Unable to get builds information from server, status code: {}'.format(str(response.status_code)))

    builds_info = {}

    doc = etree.fromstring(answer.strip())

    for element in doc:

        el = etree.fromstring(etree.tostring(element))

        id = str(ensure_not_single_element_list(el.xpath("//build/@id")))
        logg('id', id)

        number = str(ensure_not_single_element_list(el.xpath("//build/@number")))
        logg('number', number)

        branch = ensure_not_single_element_list(el.xpath("//build/@branchName"))
        if branch is None:
            branch = 'default'
        logg('branch', branch)

        status = ensure_not_single_element_list(el.xpath("//build/@status"))
        logg('status', status)

        tags_count = ensure_not_single_element_list(el.xpath("//tags/@count"))
        logg('tags_count', tags_count)

        if tags_count > 0:
            tags = get_tags(tcserver_info, id)
        else:
            tags = []

        artifacts = get_artifacts(tcserver_info, id)

        comment = ensure_not_single_element_list(el.xpath("//text/text()"))
        logg('comment', comment)
        if comment is None:
            comment = ''

        build_info = BuildInfo(
            id,
            number,
            branch,
            status,
            tags,
            artifacts,
            comment,
        )

        logg('build_info', build_info)
        builds_info[number] = build_info

    return builds_info


def _wait_builds(config, tcserver_info, build_ids, comments):
    log_new('_wait_builds')

    logg('build_ids', build_ids)
    logg('comments', comments)

    if len(build_ids) == 0:
        return {}

    # note: single-liners do not work for lists with single element

    build_numbers = {}
    for build_id in build_ids:
        build_numbers[build_id] = None

    logg('initial build_numbers', build_numbers)

    build_comments = {}
    for build_id, comment in zip(build_ids, comments):
        build_comments[build_id] = comment

    logg('initial build_comments', build_comments)

    wait_key = True
    counter = 0
    wait_period = 5
    wait_limit = int(round(config.GLOBAL_TIMEOUT_SEC / wait_period))
    build_creation_wait_limit = int(round(config.TC_BUILD_CREATION_TIMEOUT_SEC / wait_period))

    while wait_key:
        counter += 1
        time.sleep(wait_period)
        log('waiting period: {}'.format(str(counter)))

        for build_id in build_ids:

            if build_numbers[build_id] is None:
                logg('build_id', build_id)

                url = '{}/app/rest/builds/?locator=buildType:{},id:{}'. \
                    format(tcserver_info.url, tcserver_info.project, str(build_id))
                logg('url', url)
                response = requests.get(url, auth=(tcserver_info.login, tcserver_info.password))
                answer = response.content
                logg('answer', answer)

                doc = etree.fromstring(answer.strip())

                build_state = ensure_not_single_element_list(doc.xpath("//build/@state"))
                logg('build_state', build_state)

                if build_state == 'finished':
                    log('build is finished')

                    build_number = ensure_not_single_element_list(doc.xpath("//build/@number"))

                    if build_number is None:
                        if counter >= build_creation_wait_limit:
                            raise Exception('Build creation timeout: {} sec'.format(
                                str(config.TC_BUILD_CREATION_TIMEOUT_SEC)))

                    logg('build_number', build_number)
                    build_numbers[build_id] = build_number

                    logg('build_comments[build_id]', build_comments[build_id])
                    create_tag(tcserver_info, build_id, build_comments[build_id])

        if None not in build_numbers.values():
            wait_key = False
        if counter >= wait_limit:
            raise Exception('Build wait timeout: {} sec'.format(str(config.GLOBAL_TIMEOUT_SEC)))

    time.sleep(wait_period)

    logg('resulted build_numbers', build_numbers)

    logg('resulted build_comments', build_comments)

    return build_numbers


def start_build(tcserver_info, tc_project_parameters_dict, branch, comment):
    log_new('start_build')

    url = tcserver_info.url + '/app/rest/buildQueue/'
    logg('url', url)

    parameters_row = ''
    for parameter_name, parameter_value in tc_project_parameters_dict.iteritems():
        parameters_row += '<property name="{}" value="{}"/>'.format(parameter_name, parameter_value)
    tc_project_parameters = '<properties>{}</properties>'.format(parameters_row)

    comment = '<comment><text>{}</text></comment>'.format(comment)

    if 'default' in branch.lower():
        branch = escape(branch)

    template = '<build branchName="{}"><buildType id={}/>{}{}</build>'.format(branch, '{id}',
                                                                              tc_project_parameters, comment)

    logg('template', template)

    headers = {'Content-Type': 'application/xml'}

    data = template.format(id=quoteattr(tcserver_info.project))

    logg('data', data)

    logg('login | password', '{} | {}'.format(tcserver_info.login, tcserver_info.password))

    response = requests.post(url, headers=headers, data=data, auth=(tcserver_info.login, tcserver_info.password),
                             timeout=10)

    answer = response.content

    logg('answer', answer)

    if response.status_code != 200:
        raise Exception(
            'Unable to start build, status code: {}'.format(str(response.status_code)))

    doc = etree.fromstring(answer.strip())
    values = doc.xpath("//build/@id")
    build_id = values[0]

    logg('values', values)
    logg('build_id', build_id)

    return build_id
