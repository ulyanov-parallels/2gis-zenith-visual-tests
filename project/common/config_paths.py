# coding: utf8


import os


class PathConfig():
    """
    CONFIG PATHS
    """

    ENV_CHECKOUT_DIR = os.path.abspath(os.path.join(__file__, "..", "..", ".."))

    ENV_CONFIG_DIR = os.path.join(ENV_CHECKOUT_DIR, 'config')

    ENV_PROJECT_DIR = os.path.join(ENV_CHECKOUT_DIR, 'project')

    ENV_TESTS_DIR = os.path.join(ENV_CHECKOUT_DIR, 'tests')

    ENV_SCRIPTS_DIR = os.path.join(ENV_CHECKOUT_DIR, 'scripts')

    ENV_ADB_SCRIPTS_DIR = os.path.join(ENV_SCRIPTS_DIR, 'adb')

    ENV_SHELL_SCRIPTS_DIR = os.path.join(ENV_SCRIPTS_DIR, 'shell')

    ENV_WEB_REPORT_DIR = os.path.join(ENV_CHECKOUT_DIR, 'web_report')

    ENV_BASE_DATA_DIR = os.path.join(ENV_CHECKOUT_DIR, 'base_data')

    TEMP_DIR = os.path.join(ENV_CHECKOUT_DIR, 'temp')

    TEMP_DATA_DIR = os.path.join(TEMP_DIR, 'data')

    TEMP_RESULTS_DIR = os.path.join(TEMP_DIR, 'results')

    TEMP_ARTIFACTS_DIR = os.path.join(TEMP_DIR, 'artifacts')

    TEMP_ARTIFACTS_DATA_DIR = os.path.join(TEMP_ARTIFACTS_DIR, 'data')

    TEMP_ARTIFACTS_LOGS = os.path.join(TEMP_ARTIFACTS_DIR, 'logs')

    TEMP_ARTIFACTS_SCREENS = os.path.join(TEMP_ARTIFACTS_DIR, 'screens')

    ANDROID_MAIN_DIR = '/sdcard/Download'

    def define_android_paths(self, base_name='_default'):

        self.ANDROID_WORK_DIR = '{}/{}'.format(self.ANDROID_MAIN_DIR, base_name)

        self.ANDROID_SCREENS_DIR = '{}/screens'.format(self.ANDROID_WORK_DIR)

        self.ANDROID_TEMP_DIR = '{}/temp'.format(self.ANDROID_WORK_DIR)

        self.ANDROID_MODELS_DIR = '{}/models'.format(self.ANDROID_WORK_DIR)

        self.ANDROID_DYNAMIC_MODELS_DIR = '{}/dynamic_models'.format(self.ANDROID_WORK_DIR)
