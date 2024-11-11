#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import pprint
print('enter aprs api key')
api_key = input()
print('enter geonames api key/username')
gapi_key = input()
print('enter your call sign')
callsign = input()
now = datetime.datetime.now()
first_run = now.day + now.hour + now.minute -1

cache_py = open('aprs_data_' + callsign + '.py','w')
cache_py.write('api_key =' + pprint.pformat(api_key) + '\n')
cache_py.write('gapi_key =' + pprint.pformat(gapi_key) + '\n')
cache_py.write('lastrun =' + pprint.pformat(first_run) + '\n')
cache_py.write('callsign  =' + pprint.pformat(callsign) + '\n')
cache_py.close()

