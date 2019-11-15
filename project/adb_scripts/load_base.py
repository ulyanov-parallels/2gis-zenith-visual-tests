# coding: utf8

"""
LOAD BASE
"""

import os
from adb_prototype import get_adb_client, AdbDevice
from common.logger import log_new, logg


def adb_load_base(config, parameters):
    log_new('load_base')

    [
        base,
        device_name,
    ] = parameters

    base_name = os.path.basename(base)

    logg('base', base)
    logg('device_name', device_name)

    adb_client = get_adb_client()

    adb_device = AdbDevice(device_name, config, adb_client)

    adb_device.echo('Recreating work dir {}'.format(config.ANDROID_WORK_DIR))
    if config.ANDROID_WORK_DIR == config.ANDROID_MAIN_DIR:
        raise Exception('Incorrect work dir: {}'.format(config.ANDROID_WORK_DIR))
    adb_device.delete_path_on_android(config.ANDROID_WORK_DIR)
    adb_device.create_dir_on_android(config.ANDROID_WORK_DIR)

    adb_device.echo('Loading base to Android device: {}'.format(device_name))
    adb_device.copy_file_to_android(base, '{}/{}'.format(config.ANDROID_WORK_DIR, base_name))

    adb_device.list_dir_content_on_android(config.ANDROID_WORK_DIR)

    adb_device.echo('Loading base finished')
