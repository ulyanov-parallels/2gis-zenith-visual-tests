# coding: utf8


from collections import namedtuple
import os

from common.config_lib import read_file
from common.logger import log, log_new, logg
from image_comparison import ImageSet
from log_comparison import get_testcase_name, LogSet


ParameterInfo = namedtuple('ParameterInfo', ['name', 'type', 'value'])
"""
Container with parameters information (for webreport)

:param name: parameter's name
:type name: str
:param type: parameter's type: cb (independent for current and baseline), common (allways same for both datasets)
:type type: str
:param value: parameter's value: list for cb type [current_value, baseline_value], single value for common type
:type value: list[str]
"""

ScreenInfo = namedtuple('ScreenInfo', [
    'screen_name',
    'testcase_id',
    'testcase_name',
    'screen_number',
    'feature_test',
    'location',
    'scale',
    'angle',
    'diff_sum',
    'status'])
"""
Container with particular screenshot information (for webreport)

:param screen_name: full screenshot name without extension
:type screen_name: str
:param testcase_id: subj usually in format test_suite_name + number_of_testcase_in_test_suite
:type testcase_id: str
:param testcase_name: screenshot name w/o scale, angle and extension
:type testcase_name: str
:param screen_number: number of screenshot in particular testcase
:type screen_number: str
:param feature_test: feature-test name
:type feature_test: str
:param location: name of location
:type location: str
:param scale: z value
:type scale: str
:param angle: angle (in horizontal plane) value
:type angle: str
:param diff_sum: sum of difference values of all pixels in rgb units
:type diff_sum: str
:param status: status (FAILED/PASSED)
:type status: str
"""


def add_divider(lines):
    log_new('add_divider')
    return lines + ['<a>---------------------------</a><br>']


def create_parameter_rows(parameter_type, lines, parameters_set):
    log_new('create_parameter_rows')

    assert isinstance(parameter_type, str)
    assert isinstance(lines, list)
    assert isinstance(parameters_set, list)
    
    new_lines = []
    
    for parameter_info in parameters_set:
        assert isinstance(parameter_info, ParameterInfo)
        
        if parameter_type == parameter_info.type:
            
            for line in lines:
                if '$parameter_name$' in line:
                    new_line = line.replace('$parameter_name$', parameter_info.name)
                    
                elif '_value$' in line:
                    
                    if parameter_type == 'cb':
                        assert isinstance(parameter_info.value, list)
                        if '$current_value$' in line:
                            new_line = line.replace('$current_value$', str(parameter_info.value[0]))
                            
                        elif '$baseline_value$' in line:
                            new_line = line.replace('$baseline_value$', str(parameter_info.value[1]))
                            
                    elif parameter_type == 'common':
                        assert not isinstance(parameter_info.value, list)
                        if '$common_value$' in line:
                            new_line = line.replace('$common_value$', str(parameter_info.value))
                else:
                    new_line = line
                    
                new_lines.append(new_line)
            
    return new_lines


def create_stat_rows(lines, stat_cont):
    log_new('create_stat_rows')
    
    assert isinstance(lines, list)
    assert isinstance(stat_cont, tuple)
    
    new_lines = []
    for name, value in stat_cont._asdict().iteritems():
        for line in lines:
            if '$stat_metric$' in line:
                new_line = line.replace('$stat_metric$', str(name).replace('_', ' '))
            elif '$stat_value$' in line:
                new_line = line.replace('$stat_value$', str(value))
            else:
                new_line = line
            new_lines.append(new_line)
            
    return new_lines


def create_log_rows(lines, log_cont, config):
    log_new('create_log_rows')
    
    assert isinstance(lines, list)
    assert isinstance(log_cont, list)
    
    if not config.REPORT_LOGS:
        return []

    new_lines = []
    
    # todo: (not MVP) create statistics based on testcases with subcases
    # todo: where log parts comparison and each screen comparison will be separate subcase
    for log_set in log_cont:
        assert isinstance(log_set, LogSet)
        assert log_set.correct is not None
    
        if log_set.diff is None \
                and log_set.current is not None \
                and log_set.baseline is not None:
            status = 'PASSED'
        else:
            status = 'FAILED'

        if status == 'FAILED' or (status == 'PASSED' and config.REPORT_IDENTICAL_LOGS):
            
            for line in lines:
            
                if '<a>$' in line:
                    if 'info' in line:
                        new_lines.append('<a name=log_{}>log part:</a>'.format(log_set.correct.replace(' ', '_')))
                        new_lines.append(line.replace('$info$', log_set.correct))
                        new_lines = add_divider(new_lines)
                        new_lines.append('<a>status: {}</a><br>'.format(status))
                        if log_set.correct != 'before' and log_set.correct != 'after':
                            new_lines.append('<br><a href="report.html#screen_{}">screens</a><br>'.
                                             format(log_set.correct.replace(' ', '_')))
                    else:
        
                        for itype in config.RESULT_TYPES:
                            if '${}_'.format(itype) in line:
        
                                if itype == 'current':
                                    log_content = log_set.current
                                elif itype == 'baseline':
                                    log_content = log_set.baseline
                                elif itype == 'diff':
                                    log_content = log_set.diff
        
                                if log_content is None:
                                    if itype == 'diff':
                                        text = ' No diff created'
                                    else:
                                        text = ' Lost {}: {}'.format(itype, log_set.correct)

                                    new_lines.append('<div class ="t_normal">')   # no highlight
                                    new_lines.append('<a>{}</a>'.format(text))
                                    new_lines.append('</div>')
                                else:
                                    toggle_key = False
                                    for row in log_content:
                                        
                                        if not str(row).startswith('*'):
                                            
                                            if toggle_key:
                                                new_lines.append('</div>')
                                                toggle_key = False
                                                
                                            if str(row).startswith('+'):
                                                new_lines.append('<div class ="t-green">')
                                            elif str(row).startswith('-'):
                                                new_lines.append('<div class ="t-red">')
                                            elif str(row).startswith('?'):
                                                new_lines.append('<div class ="t-normal">')
                                            else:
                                                new_lines.append('<div class ="t-collapse">')
                                                
                                            new_lines.append('<a>{}</a>'.format(row))
                                            new_lines.append('</div>')
                                            
                                        else:
                                            if not toggle_key:
                                                new_lines.append(
                                                    '<div class="collapse" data-toggle="offcanvas" ' +
                                                    'data-alt-text="   . . . EXPAND . . .   ">')
                                                toggle_key = True

                                            new_lines.append('<div class ="collapse">')
                                            new_lines.append('<a>{}</a>'.format(row.lstrip('*')))
                                            new_lines.append('</div>')
                
                else:
                    new_lines.append(str(line))
    
    return new_lines


def create_image_rows(lines, image_cont, status, config):
    log_new('create_image_column')
    
    assert isinstance(lines, list)
    assert isinstance(image_cont, list)
    
    if not config.REPORT_SCREENS:
        return []
    
    def get_image_set_info(image_set):
        log_new('get_image_set_info')
        
        correct_name = image_set.correct
        info_set = correct_name.rstrip('.png').split('_')
        screen_name = correct_name.rstrip('.png')

        if image_set.diff is not None:
    
            diff_name = os.path.basename(image_set.diff)
            logg('diff_name', diff_name)
            diff_info_set = diff_name.rstrip('.png').split('_')
    
            if len(diff_info_set) == 7:
                diff_sum = diff_info_set[6]
            else:
                raise Exception(
                    'Incorrect format of diff name: number of "_"-devided items = {} (expected 7)'.format(
                        len(diff_info_set)))
        else:
            diff_sum = None
        
        if len(info_set) == 6:
            
            result = ScreenInfo(
                screen_name,
                info_set[0],
                get_testcase_name(screen_name),
                info_set[1].replace('scr', ''),
                info_set[2],
                info_set[3],
                info_set[4],
                info_set[5],
                diff_sum,
                status[screen_name],
            )
            
        else:
            raise Exception(
                'Incorrect format of screenshot name: number of "_"-devided items = {} (expected 6)"'.
                    format(len(info_set)))
           
        return result
        
   
    new_lines = []
    new_lines.append('')

    for image_set in image_cont:
        assert isinstance(image_set, ImageSet)

        info = get_image_set_info(image_set)
        
        if info.status == 'PASSED' and not config.REPORT_IDENTICAL_SCREENS:
            log('skipping identical screens set')
        else:
            
            for line in lines:
                new_line = line
                
                if 'info' in new_line:
                    for name, value in info._asdict().iteritems():
                        if name == 'testcase_name':
                            new_lines.append('<a name=screen_{}>testcase name:</a><br><a>{}</a><br>'.
                                             format(value.replace(' ', '_'), value))
                        elif name == 'screen_name':
                            new_lines.append(new_line.replace('$info$', value))
                            new_lines = add_divider(new_lines)
                        else:
                            new_lines.append(
                                new_line.replace('$info$'.format(itype), '{}: {}'.
                                                 format(name.replace('_', ' '), value)))
                            if name == 'angle':
                                new_lines = add_divider(new_lines)
                    new_lines.append('<a href="report.html#log_{}">logs</a>'.
                                     format(info.testcase_name.replace(' ', '_')))
                    
                    new_line = ''
                
                for itype in config.RESULT_TYPES:
                    if '${}_'.format(itype) in line:
                    
                        if itype == 'current':
                            link = image_set.current
                        elif itype == 'baseline':
                            link = image_set.baseline
                        elif itype == 'diff':
                            link = image_set.diff
                            
                        if link is None:
                            if itype == 'diff':
                                text = ' No diff created'
                            else:
                                text = ' Lost {}: {}'.format(itype, image_set.correct)
                                
                        else:
                            link = link.replace(config.TEMP_DIR, '').lstrip('\\')  # path localization for TeamCity
                            text = str(os.path.basename(link))
                            
                        if 'link' in new_line:
                            new_line = new_line.replace('${}_link$'.format(itype), str(link))
                            
                        if 'text' in new_line:
                            new_line = new_line.replace('${}_text$'.format(itype), text)
    
                new_lines.append(new_line)
        
    return new_lines


def create_webreport(image_cont, log_cont, stat_cont, status, parameters, config):
    """
    :param image_cont: container with image data
    :type image_cont: ImageSet
    :param log_cont: container with log data
    :type log_cont: LogSet
    :param stat_cont: container with statistics data
    :type stat_cont: StatCont
    :param status: status info for subcases (image sets)
    :type status: dict{str: str}
    :param parameters: container with parameters
    :type parameters: argparse.ArgumentParser().parse_args()
    :param config: configuration
    :type config: Config
    :return: webreport content
    :rtype: list[str]
    """
    log_new('create_webreport')
    
    assert isinstance(image_cont, list)
    assert isinstance(log_cont, list)
    assert isinstance(parameters, object)
    assert isinstance(config, object)
    
    report_template = config.WEB_REPORT_TEMPLATE
    assert isinstance(report_template, str)

    parameters_set = [
        ParameterInfo('build number', 'cb', [parameters.current_build, parameters.baseline_build]),
        ParameterInfo('test build number', 'cb', [parameters.current_test_build, parameters.baseline_test_build]),
        ParameterInfo('test name', 'common', parameters.test_name),
        ParameterInfo('base name', 'common', parameters.base_name),
        ParameterInfo('device name', 'common', parameters.device_name),
        ParameterInfo('rgb threshold', 'common', parameters.rgb_threshold),
        ParameterInfo('size threshold', 'common', parameters.size_threshold)
    ]
    
    log_new('**********')
    log('Parameters')
    log('type * name * value')
    for parameter in parameters_set:
        parameter_type = str(parameter.type)
        parameter_name = str(parameter.name)
        parameter_value = str(parameter.value)
        log('  *  '.join([parameter_type, parameter_name, parameter_value]))
    log('**********')
    
    log_new('**********')
    log('Image sets')
    log('current * baseline * diff')
    for image_set in image_cont:
        current_screen = str(image_set.current)
        baseline_screen = str(image_set.baseline)
        diff_screen = str(image_set.diff)
        log('  *  '.join([current_screen, baseline_screen, diff_screen]))
    log('**********')
    
    template = read_file(report_template)
    report = []
    allowed = True
    title = 'Zenith visual results comparison: {}(current) vs {}(baseline)'.\
        format(parameters.current_build, parameters.baseline_build)
   
    for line in template:
        
        if 'row_begin -->' in line:
            allowed = False
            custom_lines = []
            
        elif 'row_end -->' in line:
            allowed = True
            
            if 'parameter' in line:
                for type_name in config.PARAMETER_TYPES:
                    if '<!-- {}_'.format(type_name) in line:
                        report += create_parameter_rows(type_name, custom_lines, parameters_set)
                        
            elif 'stat' in line:
                report += create_stat_rows(custom_lines, stat_cont)
                
            elif 'images' in line:
                report += create_image_rows(custom_lines, image_cont, status, config)
                
            elif 'log' in line:
                report += create_log_rows(custom_lines, log_cont, config)
            
        elif '$title$' in line:
            new_line = line.replace('$title$', title)
            
        else:
            new_line = line
            
        if allowed:
            report.append(new_line)
        else:
            custom_lines.append(line)
       
    return report
