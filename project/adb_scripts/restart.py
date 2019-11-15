# coding: utf8

"""
ADB RESTART
"""

from adb_prototype import kill_adb, start_adb, reconnect_offline

from common.logger import log_new


def adb_restart(config):
    log_new('adb_restart')

    # use only at global start!

    kill_adb(config)
    start_adb(config)
    reconnect_offline(config)
