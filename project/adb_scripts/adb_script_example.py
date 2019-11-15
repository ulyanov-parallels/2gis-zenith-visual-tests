# coding: utf8

"""
ADB PROTOTYPE SCRIPT EXAMPLE
"""

from adb_prototype import simple_wait, kill_adb, start_adb, reconnect_offline, get_adb_client, AdbDevice

from common.configurator import Config
from common.logger import log_new


class PrototypeConfig(Config):
    """
    Prototype test configuration
    """

    DATA_DIR = 'D:/Autotests/temp/proto_test_data'

    RESULT_DIR = 'D:/Autotests/temp/proto_test_data/result'

    APK_PATH = '{}/ZenithCartoScriptingTestApp-debug.apk'.format(DATA_DIR)

    SH_SCRIPT = 'run.sh'

    TEST_DATA = ['moscow_mobile.2gis',
                 'OfflineDynamic.2gis',
                 'regression.json',
                 'Samsung_Galaxy_S4.config',
                 'run.sh',
                 'test.txt']

    ANDROID_WORK_DIR = '{}/{}'.format(Config.ANDROID_MAIN_DIR, 'proto')

    ANDROID_SCREENS_DIR = '{}/{}'.format(ANDROID_WORK_DIR, 'screens')

    ANDROID_TEMP_DIR = '{}/{}'.format(ANDROID_WORK_DIR, 'temp')

    WAIT_REBOOT_SEC = 120

    WAIT_INSTALL_SEC = 120

    WAIT_LOG = 30

    SH_ARGS = ['5',
               '600',
               ANDROID_WORK_DIR,
               'regression.json',
               Config.APP_NAME_RUN,
               'Samsung_Galaxy_S4.config',
               'regression.json',
               'ZenithNewTestApp.log']


def get_input_parameters():
    """
    Prototype test parameters
    """

    parameters = {
        'device_name': 'Samsung_Galaxy_S4'
    }

    return parameters


def adb_script(device_name, parameters, config):
    """
    Python adb script example
    """

    log_new('adb_script')

    restart_key = False
    # use only at global start
    if restart_key:
        kill_adb(config)
        start_adb(config)

    reconnect_offline(config)

    adb_client = get_adb_client()

    adb_device = AdbDevice(device_name, config, adb_client)

    adb_device.echo('Running test on Android device: {}'.format(parameters['device_name']))

    adb_device.clear_logcat()

    adb_device.reboot_device()

    simple_wait(config.WAIT_REBOOT_SEC)

    reconnect_offline(config)

    adb_device.delete_path_on_android(config.ANDROID_WORK_DIR)
    adb_device.create_dir_on_android(config.ANDROID_WORK_DIR)
    adb_device.create_dir_on_android(config.ANDROID_SCREENS_DIR)
    adb_device.create_dir_on_android(config.ANDROID_TEMP_DIR)

    for data_file in config.TEST_DATA:
        adb_device.copy_file_to_android('{}/{}'.format(config.DATA_DIR, data_file),
                                        '{}/{}'.format(config.ANDROID_WORK_DIR, data_file))

    adb_device.list_dir_content_on_android(config.ANDROID_WORK_DIR)

    if adb_device.check_app_installed(config.APP_NAME_INSTALL):
        adb_device.uninstall_app(config.APP_NAME_INSTALL)

    adb_device.install_apk(config.APK_PATH)

    simple_wait(config.WAIT_INSTALL_SEC)

    adb_device.run_sh_script('{}/{}'.format(config.ANDROID_WORK_DIR, config.SH_SCRIPT), ' '.join(config.SH_ARGS))

    for data_file in config.TEST_DATA:
        adb_device.copy_file_to_desktop('{}/{}'.format(config.ANDROID_WORK_DIR, data_file),
                                        '{}/{}'.format('{}_{}'.format(config.RESULT_DIR, parameters['device_name']),
                                                       data_file))

    for data_file in config.TEST_DATA:
        adb_device.delete_path_on_android('{}/{}'.format(config.ANDROID_WORK_DIR, data_file))

    adb_device.list_dir_content_on_android(config.ANDROID_WORK_DIR)

    adb_device.get_logcat()

    adb_device.get_logcat()

    simple_wait(config.WAIT_LOG)

    adb_device.echo('Test finished')


def main():
    log_new('main')
    config = PrototypeConfig()
    parameters = get_input_parameters()
    adb_script(parameters['device_name'], parameters, config)


main()  #local run only