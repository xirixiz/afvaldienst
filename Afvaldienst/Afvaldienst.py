# -*- coding: utf-8 -*-

"""
This library is meant to interface with mijnafvalwijzer.nl and/or afvalstoffendienstkalender.nl
It is meant to use with home automation projects like Home Assistant.

Author: Bram van Dartel (https://github.com/xirixiz/)

## Usage - see README.rst

"""

import re
import requests
import json
from datetime import date, datetime, timedelta

trash_json = {}

class Afvaldienst(object):
    def __init__(self, provider, zipcode, housenumber, suffix, count_today):
        self.provider = provider
        self.housenumber = housenumber
        self.suffix = suffix
        self.countToday = count_today
        _zipcode = re.match('^\d{4}[a-zA-Z]{2}', zipcode)
        if _zipcode:
            self.zipcode = _zipcode.group()
        else:
            print("Zipcode has a incorrect format. Example: 1111AA")

        _providers = ('mijnafvalwijzer', 'afvalstoffendienstkalender')
        if self.provider not in _providers:
            print("Invalid provider: {}, please verify".format(self.provider))
        else:
            if self.provider == 'mijnafvalwijzer':
                self.apikey = '5ef443e778f41c4f75c69459eea6e6ae0c2d92de729aa0fc61653815fbd6a8ca'
            if self.provider == 'afvalstoffendienstkalender':
                self.apikey = '5ef443e778f41c4f75c69459eea6e6ae0c2d92de729aa0fc61653815fbd6a8ca'

        # self.date_today = '2020-06-16'
        self.date_today = datetime.today().strftime('%Y-%m-%d')
        today_to_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=1)
        self.date_tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')
        day_after_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=2)
        self.date_dat = datetime.strftime(day_after_tomorrow, '%Y-%m-%d')

        self._jsonData = self.__get_data_json()
        self._trashTypes = self.__get_data_trash_types()
        self._trashScheduleFull, self._trashScheduleToday, self._trashScheduleTomorrow, self._trashScheduleDAT, self._trashNextPickupItem, self._trashNextPickupDate, self._trashFirstNextInDays = self.__get_trashschedule()

    def __get_data_json(self):
        jsonUrl = 'https://api.{}.nl/webservices/appsinput/?apikey={}&method=postcodecheck&postcode={}&street=&huisnummer={}&toevoeging={}&app_name=afvalwijzer&platform=phone&afvaldata={}&langs=nl'.format(self.provider, self.apikey, self.zipcode, str(self.housenumber), self.suffix, self.date_today)

        try:
            rawResponse = requests.get(jsonUrl)
        except requests.exceptions.RequestException as err:
            raise ValueError(err)
            raise ValueError('Provider URL not reachable or a different error appeared. Please verify the url:' + jsonUrl + 'manually in your browser. Text mixed with JSON should be visible.')

        try:
            jsonResponse = rawResponse.json()
        except ValueError:
            raise ValueError('No JSON data received from ' + jsonUrl)

        try:
            jsonData = (jsonResponse['ophaaldagen']['data'] + jsonResponse['ophaaldagenNext']['data'])
            return jsonData
        except ValueError:
            raise ValueError('Invalid JSON data received from ' + jsonUrl)

    def __get_data_trash_types(self):
        trashTypes = []
        for item in self._jsonData:
            trash = item["nameType"].strip()
            if trash not in trashTypes:
                trashTypes.append(trash)

        return trashTypes

    def __get_trashschedule(self):
        trashType = {}
        trashNextDays = {}
        trashNextItem = {}
        trashToday = {}
        trashTomorrow = {}
        trashDAT = {}

        multiTrashNextPickupItem = []
        multiTrashToday = []
        multiTrashTomorrow = []
        multiTrashDAT = []

        trashNextPickupDate = []
        trashFirstNextInDays = []
        trashNextPickupItem = []
        trashScheduleToday = []
        trashScheduleTomorrow = []
        trashScheduleDAT = []
        trashScheduleFull = []

        trashTypesExtended = ['today', 'tomorrow', 'first_next_in_days', 'first_next_item', 'first_next_date']
        trashTypesExtended.extend(self._trashTypes)

        if self.countToday.casefold() in ('true', 'yes'):
            countToday = self.date_today
        else:
            countToday = self.date_tomorrow

        # Some date count functions for next stuff
        def d(s):
            [year, month, day] = map(int, s.split('-'))
            return date(year, month, day)

        def days(start, end):
            return (d(end) - d(start)).days

        def __gen_json(x, y):
            global trash_json
            trash_json = {}
            trash_json['key'] = x.strip()
            trash_json['value'] = y.strip()
            return trash_json

        for name in trashTypesExtended:
            for item in self._jsonData:
                name = item["nameType"]
                dateConvert = datetime.strptime(item['date'], '%Y-%m-%d').strftime('%d-%m-%Y')

                if name not in trashType:
                    if item['date'] >= self.date_today:
                        trash = {}
                        trashType[name] = item["nameType"].strip()
                        trash['key'] = item['nameType'].strip()
                        trash['value'] = dateConvert
                        trash['days_remaining'] = (days(self.date_today, item['date']))
                        trashScheduleFull.append(trash)

                    if item['date'] >= countToday:
                        if len(trashNextDays) == 0:
                            trashType[name] = "first_next_in_days"
                            trashNextDays['key'] = "first_next_in_days"
                            trashNextDays['value'] = (days(self.date_today, item['date']))
                            trashFirstNextInDays.append(trashNextDays)
                        if len(trashNextItem) == 0:
                            trashType[name] = "first_next_item"
                            trashNextItem['key'] = "first_next_item"
                            trashNextItem['value'] = item['nameType'].strip()
                            trashNextPickupItem.append(trashNextItem)
                            dateCheck = item['date']
                        if len(trashNextItem) != 0:
                            if item['date'] == dateCheck:
                                multiTrashNextPickupItem.append(item['nameType'].strip())
                                trashNextItem['value'] = ', '.join(multiTrashNextPickupItem).strip()
                        if len(trashNextPickupDate) == 0:
                            __gen_json('first_next_date', dateConvert)
                            trashNextPickupDate.append(trash_json)

                    if item['date'] == self.date_today:
                        if len(trashScheduleToday) == 0:
                            trashType['today'] = "today"
                            trashToday['key'] = "today"
                            trashToday['value'] = item['nameType'].strip()
                            trashScheduleToday.append(trashToday)
                        if len(trashScheduleToday) != 0:
                            multiTrashToday.append(item['nameType'].strip())
                            trashToday['value'] = ', '.join(multiTrashToday).strip()

                    if item['date'] == self.date_tomorrow:
                        if len(trashScheduleTomorrow) == 0:
                            trashType[name] = "tomorrow"
                            trashTomorrow['key'] = "tomorrow"
                            trashTomorrow['value'] = item['nameType'].strip()
                            trashScheduleTomorrow.append(trashTomorrow)
                        if len(trashScheduleTomorrow) != 0:
                            multiTrashTomorrow.append(item['nameType'].strip())
                            trashTomorrow['value'] = ', '.join(multiTrashTomorrow).strip()

                    if item['date'] == self.date_dat:
                        if len(trashScheduleDAT) == 0:
                            trashType[name] = "day_after_tomorrow"
                            trashDAT['key'] = "day_after_tomorrow"
                            trashDAT['value'] = item['nameType'].strip()
                            trashScheduleDAT.append(trashDAT)
                        if len(trashScheduleDAT) != 0:
                            multiTrashDAT.append(item['nameType'].strip())
                            trashDAT['value'] = ', '.join(multiTrashDAT).strip()

            if len(trashScheduleToday) == 0:
                trashType[name] = "today"
                trashToday['key'] = "today"
                trashToday['value'] = "None"
                trashScheduleToday.append(trashToday)

            if len(trashScheduleTomorrow) == 0:
                trashType[name] = "tomorrow"
                trashTomorrow['key'] = "tomorrow"
                trashTomorrow['value'] = "None"
                trashScheduleTomorrow.append(trashTomorrow)

            if len(trashScheduleDAT) == 0:
                trashType[name] = "day_after_tomorrow"
                trashDAT['key'] = "day_after_tomorrow"
                trashDAT['value'] = "None"
                trashScheduleDAT.append(trashDAT)

        return trashScheduleFull, trashScheduleToday, trashScheduleTomorrow, trashScheduleDAT, trashNextPickupItem, trashNextPickupDate, trashFirstNextInDays

    @property
    def trash_raw_json(self):
        """Return both the pickup date and the container type."""
        return self._jsonData

    @property
    def trash_schedulefull_json(self):
        """Return both the pickup date and the container type."""
        return self._trashScheduleFull

    @property
    def trash_schedule_next_days_json(self):
        """Return both the pickup date and the container type."""
        return self._trashFirstNextInDays

    @property
    def trash_schedule_today_json(self):
        """Return both the pickup date and the container type."""
        return self._trashScheduleToday

    @property
    def trash_schedule_tomorrow_json(self):
        """Return both the pickup date and the container type."""
        return self._trashScheduleTomorrow

    @property
    def trash_schedule_dat_json(self):
        """Return both the pickup date and the container type."""
        return self._trashScheduleDAT

    @property
    def trash_schedule_next_item_json(self):
        """Return both the pickup date and the container type."""
        return self._trashNextPickupItem

    @property
    def trash_schedule_next_date_json(self):
        """Return both the pickup date and the container type."""
        return self._trashNextPickupDate

    @property
    def trash_type_list(self):
        """Return both the pickup date and the container type."""
        return self._trashTypes
