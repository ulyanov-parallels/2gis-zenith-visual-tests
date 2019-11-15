# coding: utf8


from config_lib import *
from config_paths import *


"""
NIFFLER CONFIGURATION
"""

TC_LOGIN = 'qa.robot'

TC_PASSWORD = 'test'

TC_SERVER = 'http://uk-3d-build01'

TC_SERVER_URL = '{}:8111/httpAuth'.format(TC_SERVER)

TC_SERVER_GUEST_URL = '{}/guestAuth'.format(TC_SERVER)

TC_PROJECT = 'Zenith_BenchmarkBatch'

ARTIFACT_NAME = 'Zenith-BenchmarkBatch'

ARTIFACT_FORMAT = '.zip'

ARTIFACTS = Artifacts('moscow_mobile.2gis', 'AndroidQtTestApp-debug.apk')    #now city hardcoded, will be TC parameter in future

ARTIFACT_EXTENSIONS = map(lambda name: '.' + name.split('.')[1], ARTIFACTS)

LINK_FILENAME = 'artifact_link.url'


"""
ANDROID TEST RUN CONFIGURATION
"""

SHORT_TIMEOUT_SEC = 360
GLOBAL_TIMEOUT_SEC = 7200     # 120 min
PROCESS_WAIT_TIME_STEP_SEC = 1

WAIT_SHORT_SEC = 1
WAIT_REBOOT_SEC = 30
WAIT_INSTALL_SEC = 10

ANDROID_SIDE_PERIOD_SEC = 5
ANDROID_SIDE_TIMEOUT_SEC = 5400      # 90 min

APP_NAME_INSTALL = 'ru.dublgis.zenith.qttestapp'
APP_NAME_RUN = 'ru.dublgis.zenith.qttestapp/org.qtproject.qt5.android.bindings.QtActivity'

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
    'Nokia_6': 'PLEGAR1763015311'
}
