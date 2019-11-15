# coding: utf8

"""
ADB PROTOTYPE
"""

from adb.client import Client as AdbClient
import subprocess
import time

from common.logger import log, log_new, logg


def simple_wait(period):
    log_new('_simple_wait')

    log('waiting for {} sec'.format(str(period)))
    time.sleep(float(period))


def run_process(config, cl):
    log_new('run_process')

    def wait_process(process, timeout):
        log_new('wait_process')

        start_time = time.time()
        wait_key = True
        while wait_key:
            time.sleep(config.PROCESS_WAIT_TIME_STEP_SEC)

            if process.poll() is None:  # process is running / not terminated
                current_time = time.time()
                seconds_passed = int(current_time - start_time)

                if seconds_passed > int(timeout):
                    log(' '.join(('timeout:', str(seconds_passed), 'sec')))
                    wait_key = False
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
                    log('process terminated')
            else:
                wait_key = False

    logg('cl', cl)
    process = subprocess.Popen(cl)
    wait_process(process, config.SHORT_TIMEOUT_SEC)


def kill_adb(config):
    log_new('kill_adb')
    run_process(config, 'adb kill-server')


def start_adb(config):
    log_new('start_adb')
    run_process(config, 'adb start-server')


def reconnect_offline(config):
    log_new('reconnect_offline')
    run_process(config, 'adb reconnect offline')


def get_adb_client():
    log_new('get_adb_client')
    return AdbClient(host="127.0.0.1", port=5037)   #always same


class AdbDevice:
    """
    Class for interaction with Android device via adb
    """

    def __init__(self, device_name, config, client):
        self.device_name = device_name
        self.config = config
        self.client = client
        device_code = config.DEVICE_CODES[device_name]
        logg('device_code', device_code)
        self.device = client.device(device_code)

    def _execute_shell_command_on_device(self, cl):
        log_new('_execute_shell_command_on_device')
        logg('cl', cl)
        log(self.device.shell(cl))

    def reboot_device(self):
        log_new('reboot_device')
        log(self.device_name)
        log(self.device.reboot())

    def copy_file_to_android(self, src, dest):
        log_new('copy_file_to_android')
        log('{} to {}'.format(src, dest))
        log(self.device.push(src, dest))

    def copy_file_to_desktop(self, src, dest):
        log_new('copy_file_to_desktop')
        log('{} to {}'.format(src, dest))
        log(self.device.pull(src, dest))

    def delete_path_on_android(self, path):
        log_new('delete_path_on_android')
        logg('path', path)
        cl = 'rm -r {}'.format(path)
        self._execute_shell_command_on_device(cl)

    def list_dir_content_on_android(self, dir_path):
        log_new('list_dir_content_on_android')
        logg('dir_path', dir_path)
        cl = 'ls {}'.format(dir_path)
        log('-------------------')
        self._execute_shell_command_on_device(cl)
        log('-------------------')

    def create_dir_on_android(self, dir_path):
        log_new('create_dir_on_android')
        logg('dir_path', dir_path)
        cl = 'mkdir {}'.format(dir_path)
        self._execute_shell_command_on_device(cl)

    def install_apk(self, apk_path):
        log_new('install_apk')
        logg('apk_path', apk_path)
        log(self.device.install(apk_path))

    def check_app_installed(self, app_name):
        log_new('check_app_installed')
        logg('app_name', app_name)
        result = self.device.is_installed(app_name)
        logg('result', result)
        return result

    def uninstall_app(self, app_name):
        log_new('uninstall_app')
        logg('app_name', app_name)
        log(self.device.uninstall(app_name))

    def echo(self, msg):
        log_new('echo')
        cl = 'echo {}'.format(msg)
        self._execute_shell_command_on_device(cl)

    def run_sh_script(self, sh_path, args):
        log_new('run_sh_script')
        logg('sh_path', sh_path)
        logg('args', args)
        cl = 'sh {} {}'.format(sh_path, args)
        self._execute_shell_command_on_device(cl)

    def clear_logcat(self):
        log_new('clear_logcat')
        cl = 'logcat -c'
        self._execute_shell_command_on_device(cl)

    def get_logcat(self):
        log_new('get_logcat')
        cl = 'logcat -d -v threadtime'
        self._execute_shell_command_on_device(cl)

    def set_awake(self):
        log_new('set_awake')
        # Android 5 and higher
        cl = "if [[ -z $(dumpsys power | grep 'Display Power: state'=ON) ]] && [[ -n $(dumpsys power | grep " \
             "'Display Power: state') ]]; then input keyevent 26; fi"
        self._execute_shell_command_on_device(cl)

    def set_asleep(self):
        log_new('set_asleep')
        # Android 5 and higher
        cl = "if [[ -z $(dumpsys power | grep 'Display Power: state'=OFF) ]] && [[ -n $(dumpsys power | grep " \
             "'Display Power: state') ]]; then input keyevent 26; fi"
        self._execute_shell_command_on_device(cl)

    def get_files_list_on_android(self, dir_path, extension):
        log_new('get_files_list_on_android')
        log('in dir: {} with extension: {}'.format(dir_path, extension))
        cl = 'ls {}'.format(dir_path)
        dir_content = self.device.shell(cl)
        dir_content = dir_content.encode("utf-8")
        logg('dir_content', dir_content)
        dir_content = dir_content.replace('\n', ' ')
        result = []
        for item in dir_content.split(' '):
            item = item.encode("utf-8")
            if item.strip().endswith('.{}'.format(extension)):
                result.append(item)
        return result
