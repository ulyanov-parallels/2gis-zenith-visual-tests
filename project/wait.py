# coding: utf8

"""
WAIT SCRIPT
"""

import argparse
import time


def get_parameters():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--period", type=str, required=True)
    args = parser.parse_args()
    return args


parameters = get_parameters()
period = float(parameters.period)
print('wait script: waiting for {} sec'.format(str(period)))
time.sleep(period)
print('wait script: waiting finished')
