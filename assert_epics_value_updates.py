#!/usr/bin/env python

import time, subprocess, argparse, functools
from datetime import datetime as dt

import epics # PyEpics


class Check(object):
    def __init__(self):
        self.failed_tries = []

    def register_failed_try(self, info):
        self.failed_tries.append({'ts': time.time(), 'info': info})

    def clear_failed_tries(self):
        self.failed_tries[:] = []

    def number_of_failed_tries(self, since=0):
        return len([failed_try for failed_try in self.failed_tries if failed_try['ts'] >= since])

def recv_value_update(data, **kwargs):
    """
    data will look like:
    {'pvname': 'CBM:MVD:TRB:Mvd-0xd010-DataLength.0', 'value': 42,
     'char_value': '42', 'status': 0, 'ftype': 19, 'chid': 94584834309872,
     'host': '141.2.242.225:5064', 'count': 1, 'access': 'read/write',
     'write_access': True, 'read_access': True, 'severity': 0, 'timestamp':
     1551196071.958022, 'posixseconds': 1551196071.0, 'nanoseconds': 958022546,
     'precision': None, 'units': '', 'enum_strs': None, 'upper_disp_limit': 0,
     'lower_disp_limit': 0, 'upper_alarm_limit': 0, 'lower_alarm_limit': 0,
     'lower_warning_limit': 0, 'upper_warning_limit': 0, 'upper_ctrl_limit': 0,
     'lower_ctrl_limit': 0, 'nelm': 1, 'type': 'time_long', 'typefull':
     'time_long', 'cb_info': (-999, <PV 'CBM:MVD:TRB:Mvd-0xd010-DataLength.0',
                              count=1, type=time_long, access=read/write>)}
    """
    #print(kwargs)
    data[kwargs['pvname']] = tuple(kwargs[prop] for prop in ('char_value', 'value'))

def hash_function(some_dict):
    return hash(frozenset(some_dict.items()))

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--pv', action='append', help='PV to monitor (can be used multiple times).')
    parser.add_argument('--script', help="Script to run if the PVs don't update anymore.")
    parser.add_argument('--tolerance', type=int, default=30, help="Number of times we tolerate non-changing values")
    args = parser.parse_args()

    PVs = args.pv
    data = {}

    check = Check()

    for pv in PVs:
        data[pv] = tuple()
        epics.camonitor(pv, callback=functools.partial(recv_value_update, data))
    try:
        last_hash = hash_function(data)
        while True:
            time.sleep(2)
            if hash_function(data) == last_hash:
                check.register_failed_try({})
            else:
                check.clear_failed_tries()
            if check.number_of_failed_tries() > args.tolerance:
                # no change!!! need to run script...
                print(dt.now().isoformat(), "running script because the data didn't change...")
                status = subprocess.call(args.script, shell=True) #stdout=None, stderr=None)
                check.clear_failed_tries()
    except KeyboardInterrupt:
        pass
    for pv in PVs:
        epics.camonitor_clear(pv)

if __name__ == "__main__":
    main()
