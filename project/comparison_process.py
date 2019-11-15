# coding: utf8


import sys
from common.config_lib import get_timestamp
from common.logger import log_new, logg
from comparison.process import main


if __name__ == '__main__':
    log_new('PROCESS')
    logg('started at', get_timestamp())
    retval = main()
    logg('exit code', retval)
    logg('finished at', get_timestamp())
    sys.exit(retval)
