# -*- coding: utf-8 -*-

"""
This library is meant to interface with mijnafvalwijzer.nl and/or afvalstoffendienstkalender.nl
It is meant to use with home automation projects like Home Assistant.

Author: Bram van Dartel (https://github.com/xirixiz/)

## Usage

>>> from Afvaldienst import Afvaldienst
>>> provider = 'mijnafvalwijzer'
>>> zipcode = '3825AL'
>>> housenumber = '41'
>>> suffix = ''
>>> trash = Afval(provider, zipcode, housenumber, suffix)

>>> trash.trash_raw_json
[{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}, {'nameType': 'pmd', 'type': 'pmd', 'date': '2019-12-28'}]

>>> trash.trash_next_json
[{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}

>>> trash.trash_type_list
['gft', 'kerstbomen', 'pmd', 'restafval', 'papier']

"""

import re
import requests
import json
from datetime import date, datetime, timedelta

class Afvaldienst(object):
    def __init__(self, provider, zipcode, housenumber, suffix):
        self.provider = provider
        self.housenumber = housenumber
        self.suffix = suffix
        _zipcode = re.match('^\d{4}[a-zA-Z]{2}', zipcode)
        if _zipcode:
            self.zipcode = _zipcode.group()
        else:
            raise ValueError("Zipcode has a incorrect format. Example: 3564KV")

        _providers = ('mijnafvalwijzer', 'afvalstoffendienstkalender')
        if self.provider not in _providers:
            raise ValueError("Invalid provider: {}, please verify".format(self.provider))

        self.today = datetime.today().strftime('%Y-%m-%d')
        today_to_tomorrow = datetime.strptime(self.today, '%Y-%m-%d') + timedelta(days=1)
        self.tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')

        self._json_data = self.__get_data_json()
        self._next_pickup = self.__get_data_next_pickup()
        self._trash_types = self.__get_data_trash_types()


    def __get_data_json(self):
        json_url = 'https://json.{}.nl/?method=postcodecheck&postcode={}&street=&huisnummer={}&toevoeging={}&langs=nl'.format(
            self.provider, self.zipcode, str(self.housenumber), self.suffix)
        json_response = requests.get(json_url).json()
        json_data = (json_response['data']['ophaaldagen']['data'] + json_response['data']['ophaaldagenNext']['data'])

        return json_data

    def __get_data_next_pickup(self):
        next_pickup = []
        for item in self._json_data:
            dateConvert = datetime.strptime(item['date'], '%Y-%m-%d').strftime('%d-%m-%Y')
            if item['date'] >= self.today:
                trash = {}
                trash['nameType'] = item['nameType']
                trash['type'] = item['nameType']
                trash['date'] = dateConvert
                next_pickup.append(trash)
                break

        return next_pickup

    def __get_data_trash_types(self):
        trash_types = []
        for item in self._json_data:
            trash = item["nameType"]
            if trash not in trash_types:
                trash_types.append(trash)

        return trash_types


    @property
    def trash_raw_json(self):
        """Return both the pickup date and the container type."""
        return self._json_data

    @property
    def trash_next_json(self):
        """Return both the pickup date and the container type."""
        return self._next_pickup

    @property
    def trash_type_list(self):
        """Return both the pickup date and the container type."""
        return self._trash_types