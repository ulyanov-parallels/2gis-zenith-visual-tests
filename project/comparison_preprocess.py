# coding: utf8


import sys
from common.config_lib import get_timestamp
from common.logger import log_new, logg
from comparison.preprocess import main


if __name__ == '__main__':
    log_new('PREPROCESS')
    logg('started at', get_timestamp())
    retval = main()
    logg('exit code', retval)
    logg('finished at', get_timestamp())
    sys.exit(retval)
