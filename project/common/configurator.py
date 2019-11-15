# coding: utf8


import os

from config_paths import PathConfig
from config_lib import Artifacts


class DefaultConfig(PathConfig):
    """
    Configuration of Zenith visual autotests: default
    """

    """
    NIFFLER CONFIGURATION
    """

    REMOTE_TC_LOGIN = 'qa.robot'

    REMOTE_TC_PASSWORD = 'test'

    REMOTE_TC_SERVER = 'http://uk-3d-build01'

    REMOTE_TC_SERVER_URL = '{}:8111/httpAuth'.format(REMOTE_TC_SERVER)

    REMOTE_TC_SERVER_GUEST_URL = '{}/guestAuth'.format(REMOTE_TC_SERVER)

    REMOTE_TC_PROJECT = 'Zenith_BenchmarkBatch'

    REMOTE_TC_SCOPE_DEPTH = 200  # recommended: >=200

    ARTIFACT_NAME = 'Zenith-BenchmarkBatch'

    ARTIFACT_FORMAT = '.zip'

    ARTIFACTS = Artifacts('moscow_mobile.2gis',
                          'OfflineDynamic.2gis',
                          'ZenithCartoScriptingTestApp-debug.apk')  # now city hardcoded, will be TC parameter in future
    # todo: make base_name and testapp name configurable from teamcity (not MVP)

    ARTIFACTS_X86 = Artifacts('moscow_mobile.2gis',
                              'OfflineDynamic.2gis',
                              'ZenithCartoScriptingTestApp-x86-debug.apk')  # now city hardcoded, will be TC parameter in future

    ARTIFACT_EXTENSIONS = map(lambda name: '.' + name.split('.')[1], ARTIFACTS)

    LINK_FILENAME = 'artifact_link.url'


    """
    ANDROID TEST RUN CONFIGURATION
    """

    SHORT_TIMEOUT_SEC = 600
    '''
    SHORT_TIMEOUT_SEC: short ADB-script execution timeout (in seconds)
    handling short session of interaction with Android device from desktop via ADB without test execution on device
    (with possible adb offline event);
    2nd level timeout
    '''

    GLOBAL_TIMEOUT_SEC = 9000  # 2.5 h
    '''
    GLOBAL_TIMEOUT_SEC: ADB-script execution timeout (in seconds)
    handling _main session of interaction with Android device from desktop via ADB (with possible adb offline event);
    must be long enough to cover execution time for particular scenario on slow device (Android-side timeout)
    plus time for test environment setup/teardown (data download, device restart, testapp (re)installation etc.)
    2nd level timeout
    '''
    PROCESS_WAIT_TIME_STEP_SEC = 1

    WAIT_SHORT_SEC = 1
    WAIT_REBOOT_SEC = 90
    WAIT_INSTALL_SEC = 120

    ANDROID_SIDE_PERIOD_SEC = 5
    ANDROID_SIDE_TIMEOUT_SEC = 7200  # 2 h
    '''
    ANDROID_SIDE_TIMEOUT_SEC: Android-side timeout (in seconds)
    handling testapp scenario execution (with possible crashes and hanging);
    must be long enough to cover execution time for particular scenario on slow device
    (at least 2h for regression suite, for short scenarios should be reduced properly)
    1st level timeout
    '''

    APP_NAME_INSTALL = 'ru.dublgis.zenith.cartoscriptingtestapp'
    APP_NAME_RUN = 'ru.dublgis.zenith.cartoscriptingtestapp/.ZenithCartoScriptingTestApp'

    ANDROID_SIDE_RUN_SCRIPT_NAME = 'run.sh'

    WAIT_SCRIPT_NAME = 'wait.py'

    DEVICE_CODES = {
        'Asus_ZenFone_2': 'F4AZFG12R417',
        'Samsung_Galaxy_S4': '4d009ebed4a1a1ad',
        'Samsung_Galaxy_SIII': '53b99b78',
        'LG_Nexus5': '0d1e626102b3cb9e',
        'Sony_Xperia_M5': 'YT911CJAED',
        'Sony_Xperia_S': 'CB511YMR30',
        'Lenovo_Vibe_X2': '9AF6C4F0A37EBDED',
        'Lenovo_K3_Note': 'IFRWPBEA95IBFMKZ',
        'Lenovo_Yoga_Tablet_2': 'Baytrail260BBC04',
        'Samsung_Galaxy_A5': '5210acdcfc674459',
        'Nokia_6': 'PLEGAR1763015311',
        'Samsung_Galaxy_A8': '5200244bb85775a7',
        'Samsung_Galaxy_A6+': '9397e4fb',
    }

    DEVICE_PLATFORMS = {
        'Asus_ZenFone_2': 'arm',
        'Samsung_Galaxy_S4': 'arm',
        'Samsung_Galaxy_SIII': 'arm',
        'LG_Nexus5': 'arm',
        'Sony_Xperia_M5': 'arm',
        'Sony_Xperia_S': 'arm',
        'Lenovo_Vibe_X2': 'arm',
        'Lenovo_K3_Note': 'arm',
        'Lenovo_Yoga_Tablet_2': 'x86',
        'Samsung_Galaxy_A5': 'arm',
        'Nokia_6': 'arm',
        'Samsung_Galaxy_A8': 'arm',
        'Samsung_Galaxy_A6+': 'arm',
    }

    DEFAULT_DEVICE_CONFIG = 'device.config'

    LOG_NAME = 'ZenithNewTestApp_build.log'

    DYNAMIC_MODELS = os.path.join(PathConfig.ENV_BASE_DATA_DIR, 'dynamic_models')

    MODELS = os.path.join(PathConfig.ENV_BASE_DATA_DIR, 'models')

    """
    COMPARISON CONFIGURATION
    """

    RESULTS_EXTENSIONS = {
        'screens': '.png',
        'logs': '.log',
        'scenario': '.json',
    }

    PROCESS_LOGS = True

    DEFAULT_RGB_THRESHOLD = 5

    DEFAULT_SIZE_THRESHOLD = 0

    WHITENING_RATIO = 0.3

    TEST_SCENARIO = os.path.join(PathConfig.ENV_TESTS_DIR, 'scenario.json')

    WEB_REPORT_TEMPLATE = os.path.join(PathConfig.ENV_WEB_REPORT_DIR, 'web_report_template.html')

    WEB_REPORT_LIB_DIR = os.path.join(PathConfig.ENV_WEB_REPORT_DIR, 'lib')

    TEMP_ARTIFACTS_WEBREPORT_LIB_DIR = os.path.join(PathConfig.TEMP_ARTIFACTS_DIR, 'lib')

    PARAMETER_TYPES = ['cb', 'common']

    RESULT_TYPES = ['correct', 'current', 'baseline', 'diff']

    REPORT_IDENTICAL_SCREENS = True

    REPORT_IDENTICAL_LOGS = False

    FILTER_DIFF_LOG = False

    COLLAPSE_DISTANCE_ROWS = 3

    REPORT_SCREENS = True

    # Logs comparison disabled due to heavy web-report
    # TODO:  Fix in ZNTH-2376
    REPORT_LOGS = False


class QARobotConfig(DefaultConfig):
    """
    Configuration of Zenith visual autotests: custom
    """
    def __init__(self, test_name='_main', qa_tcserver=None):
        self.test_name = test_name
        self.qa_tcserver = qa_tcserver

        self.qa_tcserver_url = '{}/httpAuth'.format(qa_tcserver)

        if self.test_name == 'regression':   # for compatability with old longer name
            self.test_name = 'regress'

        if self.test_name == 'regression2':   # for compatability with old longer name
            self.test_name = 'regress2'

        self.tag_root = 'vsl_' + test_name

        self.tag_finished = self.tag_root + '_ok'

        self.tag_broken = self.tag_root + '_br'

        self.tag_progress = self.tag_root + '_progress'

        self.tag_baseline = self.tag_root + '_base'

    QA_TC_LOGIN = 'qa.robot'

    QA_TC_PASSWORD = 'test'

    QA_TC_SCOPE_DEPTH = 300

    QA_TC_PROJECT1 = 'Autotests5_Robotic_Visual'

    QA_TC_PROJECT2 = 'Autotests5_ResultsComparison'

    QA_ROBOT_TIMEOUT_SEC = 60 * 60 * 12
    '''
    timeout_sec: QA-robot timeout (in seconds)
    handling processes beyond interactions with devices (e.g. scenario generation, results comparison etc.);
    must be long enough to cover 2 builds testing (current, baseline) on all devices included in particular
    QA-robot task
    3rd level timeout
    '''

    TC_BUILD_CREATION_TIMEOUT_SEC = 60
    '''
    timeout_sec: TC build creation after put request timeout (in seconds)
    defines waiting period for requested build appearance in queue (when number assigned to build)
    '''

    REMOTE_TC_SCOPE_DEPTH = 500  # recommended: >=200


class Config(QARobotConfig):
    """
    Configuration of Zenith visual autotests: custom
    """
    # override existing or add new parameters here (for debug, test purposes)

    pass
