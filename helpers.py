#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import requests
import json
import pathlib
import pprint
import geoname_data
import aprs_data
# constantsi
TIMEOUT = 1
class aprs:
    def __init__(self,callsign,ssid='7'):
        self.callsign = callsign
        self.id = ssid
        self.callsign_long = callsign + '-' + ssid
        self.api_key = aprs_data.api_key
    def _base_url(self, what="loc"):
        """Return the base url for endpoints."""
        if what == "msg":
            return "https://api.aprs.fi/api/get?dst=" + self.callsign + "&what="+ what + "&apikey=" + self.api_key + "&format=json"
        elif what == "loc":
            return "https://api.aprs.fi/api/get?name=" + self.callsign_long + "&what="+ what + "&apikey=" + self.api_key + "&format=json"
        else:
            return "https://api.aprs.fi/api/get?name=" + self.callsign + "&what="+ what + "&apikey=" + self.api_key + "&format=json"
    def _requests(self,what):
        input = requests.get(url=aprs(self.callsign)._base_url(what))
        return input.json()['entries']
    @property
    def get_lat(self):
        return self.get_location[0]
    @property
    def get_long(self):
        return self.get_location[1]
    @property
    def get_city(self):
        return self.get_location[2]
    @property
    def get_state(self):
        return self.get_location[3]
    @property
    def get_country(self):
        return self.get_location[4]
    @property
    def get_latlong(self):
        latlong = (self.get_location[0:2])
        return latlong 
    @property
    def get_location(self):
        now = datetime.datetime.now()
        combo = now.day + now.hour + now.minute
        if aprs_data.lastrun != combo:
            print('aprs update needed')
            data = self._requests('loc')[0]
            marker = geo(data['lat'],data['lng']).nearby
            with open('location_data.' + self.callsign + '.json' , 'w') as outfile:
                json.dump(data, outfile)
            cache_py = open('aprs_data_' + self.callsign + '.py','w')
            cache_py.write('data =' + pprint.pformat(data) + '\n')
            cache_py.write('marker =' + pprint.pformat(marker) + '\n')
            cache_py.write('lastrun =' + pprint.pformat(combo) + '\n')
            cache_py.write('api_key =' + pprint.pformat(self.api_key) + '\n')
            cache_py.close()
            app_py = open('aprs_data.py','w')
            app_py.write('lastrun =' + pprint.pformat(combo) + '\n')
            app_py.write('api_key =' + pprint.pformat(self.api_key) + '\n')
            app_py.write('data =' + pprint.pformat(data) + '\n')
            app_py.write('marker =' + pprint.pformat(marker) + '\n')
            app_py.close()
            return [data['lat'],data['lng'],marker['name'],marker['adminCode1'],marker['countryName']] 
        else:
            print('aprs rate limited last ran at: ', aprs_data.lastrun)
            print('next aprs update set for', combo)
            return [aprs_data.data['lat'],aprs_data.data['lng'],geoname_data.marker['name'],geoname_data.marker['adminCode1'],geoname_data.marker['countryName']] 
    @property
    def get_nearby(self):
        aprs = self.get_location
        lat = str(aprs[0])
        lng = str(aprs[1])
        return geo(lat,lng).get_city
    @property
    def hi(self):
        print('hi', self.callsign)
        return 
    @property
    def get_messages(self):
        messages = self._requests('msg') 
        print(messages)
        return messages
    @property
    def get_weather(self):
        wx = self._requests('wx')[0]
        print('wx from', self.callsign, (float(wx['temp'])*9/5)+32, 'degrees', wx['humidity'] +'% humidity')
        return wx
        #return self._requests('wx')
class geo:
    def __init__(self,lat,lng):
        self.lat = str(lat)
        self.lng = str(lng)
    def _base_url(self, path):
        """Return the base url for endpoints."""
        url = "http://api.geonames.org/" + path + "JSON?lat=" + self.lat + '&lng=' + self.lng + '&username='
        return url
    def _request(self, path, params=None):
        """Make the actual request and returns the parsed response."""
        url = self._base_url(path) 
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(url)
            if response:
                return response.json()
            else:
                return {'status': 'error'}
        except requests.exceptions.HTTPError:
            return {'status': 'error'}
        except requests.exceptions.Timeout:
            return {'status': 'offline'}
        except requests.exceptions.RequestException:
            return {'status': 'offline'}

    def _command(self, named_command='findNearby'):
        """Make a request for a controlling command."""
        return self._request(named_command)['geonames'][0]
    @property
    def nearby(self, path='findNearby'):
        return self._command(path)
    @property
    def get_city(self):
        return  self._command()['name'] 
    @property
    def get_state(self):
        return self._command()['adminCode1'] 
    @property
    def get_country(self):
        return self._command()['countryName'] 
