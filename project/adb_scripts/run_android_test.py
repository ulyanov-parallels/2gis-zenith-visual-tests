# coding: utf8

"""
RUN ANDROID TEST
"""

import os

from adb_prototype import simple_wait, get_adb_client, AdbDevice
from common.config_lib import prepare_directory, get_files_in_dir
from common.logger import log_new, logg


def adb_run_android_test(config, parameters):
    log_new('adb_run_android_test')

    [
    device_name,
    desktop_screens_dir,
    desktop_logs_dir,
    app_src,
    scenario_name,
    scenario_src,
    sh_script_src,
    device_config_src,
    device_config_name,
    log_name,
    dynamic_layout,
    ] = parameters

    logg('device_name', device_name)
    logg('desktop_screens_dir', desktop_screens_dir)
    logg('desktop_logs_dir', desktop_logs_dir)
    logg('app_src', app_src)
    logg('scenario_name', scenario_name)
    logg('scenario_src', scenario_src)
    logg('sh_script_src', sh_script_src)
    logg('device_config_src', device_config_src)
    logg('device_config_name', device_config_name)
    logg('log_name', log_name)
    logg('dynamic_layout', dynamic_layout)

    dynamic_layout_name = os.path.basename(dynamic_layout)

    prepare_directory(desktop_screens_dir)

    prepare_directory(desktop_logs_dir)

    adb_client = get_adb_client()

    adb_device = AdbDevice(device_name, config, adb_client)

    adb_device.echo('Running test on Android device: {}'.format(device_name))

    adb_device.set_awake()

    adb_device.echo('Rebooting device {}'.format(device_name))
    adb_device.reboot_device()

    simple_wait(config.WAIT_REBOOT_SEC)

    if adb_device.check_app_installed(config.APP_NAME_INSTALL):
        adb_device.echo('Uninstalling app {}'.format(config.APP_NAME_INSTALL))
        adb_device.uninstall_app(config.APP_NAME_INSTALL)
        simple_wait(config.WAIT_INSTALL_SEC)

    adb_device.echo('Installing apk {}'.format(app_src))
    adb_device.install_apk(app_src)
    simple_wait(config.WAIT_INSTALL_SEC)

    if not adb_device.check_app_installed(config.APP_NAME_INSTALL):
        adb_device.echo('Installing apk {} 2nd time'.format(app_src))
        adb_device.install_apk(app_src)
        simple_wait(config.WAIT_INSTALL_SEC)

    adb_device.echo('Creating work dir structure')
    adb_device.create_dir_on_android(config.ANDROID_TEMP_DIR)
    adb_device.create_dir_on_android(config.ANDROID_SCREENS_DIR)
    adb_device.create_dir_on_android(config.ANDROID_DYNAMIC_MODELS_DIR)
    adb_device.create_dir_on_android(config.ANDROID_MODELS_DIR)

    adb_device.echo('Loading test data')
    adb_device.copy_file_to_android(scenario_src, '{}/{}'.format(config.ANDROID_WORK_DIR, scenario_name))
    adb_device.copy_file_to_android(sh_script_src, '{}/{}'.format(
        config.ANDROID_WORK_DIR, config.ANDROID_SIDE_RUN_SCRIPT_NAME))
    adb_device.copy_file_to_android(device_config_src, '{}/{}'.format(config.ANDROID_WORK_DIR, device_config_name))
    adb_device.copy_file_to_android(dynamic_layout, '{}/{}'.format(config.ANDROID_WORK_DIR, dynamic_layout_name))

    dynamic_models = get_files_in_dir(config.DYNAMIC_MODELS)
    for dynamic_model in dynamic_models:
        adb_device.copy_file_to_android('{}/{}'.format(dynamic_models, dynamic_model),
                                        '{}/{}'.format(config.ANDROID_DYNAMIC_MODELS_DIR, dynamic_model))

    models = get_files_in_dir(config.MODELS)
    for model in models:
        adb_device.copy_file_to_android('{}/{}'.format(models, model),
                                        '{}/{}'.format(config.ANDROID_MODELS_DIR, model))

    adb_device.echo('ANDROID_WORK_DIR content before test:')
    adb_device.list_dir_content_on_android(config.ANDROID_WORK_DIR)

    adb_device.echo('Running app {}'.format(config.APP_NAME_INSTALL))
    sh_script_args = ' '.join((str(config.ANDROID_SIDE_PERIOD_SEC), str(config.ANDROID_SIDE_TIMEOUT_SEC),
                               config.ANDROID_WORK_DIR, scenario_name, config.APP_NAME_RUN, device_config_name,
                               scenario_name, log_name))
    logg('sh_script_args', sh_script_args)
    adb_device.run_sh_script('{}/{}'.format(
        config.ANDROID_WORK_DIR, config.ANDROID_SIDE_RUN_SCRIPT_NAME), sh_script_args)

    adb_device.echo('ANDROID_WORK_DIR content after test:')
    adb_device.list_dir_content_on_android(config.ANDROID_WORK_DIR)

    simple_wait(config.WAIT_SHORT_SEC)

    adb_device.echo('Saving results and logs')

    screens = adb_device.get_files_list_on_android(config.ANDROID_SCREENS_DIR, 'png')

    logg('screens', screens)

    for screen in screens:
        adb_device.copy_file_to_desktop('{}/{}'.format(config.ANDROID_SCREENS_DIR, screen),
                                        '{}/{}'.format(desktop_screens_dir, screen))

    adb_device.copy_file_to_desktop('{}/{}'.format(config.ANDROID_WORK_DIR, log_name),
                                    '{}/{}'.format(desktop_logs_dir, log_name))

    simple_wait(config.WAIT_SHORT_SEC)

    adb_device.echo('Test finished')

    adb_device.set_asleep()
