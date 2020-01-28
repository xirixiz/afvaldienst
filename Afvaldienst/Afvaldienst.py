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

        self.date_today = datetime.today().strftime('%Y-%m-%d')
        #self.date_today = '2019-10-25'
        today_to_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=1)
        self.date_tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')

        self._jsonData = self.__get_data_json()
        self._trashTypes = self.__get_data_trash_types()
        self._trashScheduleFull, self._trashScheduleToday, self._trashScheduleTomorrow, self._trashNextPickupItem, self._trashFirstNextInDays = self.__get_trashschedule()

    def __get_data_json(self):
        jsonUrl = 'https://json.{}.nl/?method=postcodecheck&postcode={}&street=&huisnummer={}&toevoeging={}&langs=nl'.format(
            self.provider, self.zipcode, str(self.housenumber), self.suffix)
        jsonResponse = requests.get(jsonUrl).json()
        jsonData = (jsonResponse['data']['ophaaldagen']['data'] + jsonResponse['data']['ophaaldagenNext']['data'])

        return jsonData

    def __get_data_trash_types(self):
        trashTypes = []
        for item in self._jsonData:
            trash = item["nameType"]
            if trash not in trashTypes:
                trashTypes.append(trash)

        return trashTypes

    def __get_trashschedule(self):
        trashType = {}
        trashNextDays = {}
        trashToday = {}
        trashTomorrow = {}
        multiTrashToday = []
        multiTrashTomorrow = []
        trashScheduleToday = []
        trashScheduleTomorrow = []
        trashScheduleFull = []
        trashNextPickupItem = []
        trashFirstNextInDays = []
        trashTypesExtended = ['today', 'tomorrow', 'next']
        trashTypesExtended.extend(self._trashTypes)

        # Some date count functions for next
        def d(s):
            [year, month, day] = map(int, s.split('-'))
            return date(year, month, day)

        def days(start, end):
            return (d(end) - d(start)).days

        for name in trashTypesExtended:
            for item in self._jsonData:
                name = item["nameType"]
                dateConvert = datetime.strptime(item['date'], '%Y-%m-%d').strftime('%d-%m-%Y')

                def __gen_json(name, date):
                    trash = {}
                    trash['key'] = 'first_waste_type'
                    trash['value'] = name
                    trashNextPickupItem.append(trash)

                if item['date'] >= self.date_today:
                    if len(trashNextPickupItem) == 0:
                        __gen_json(item['nameType'], dateConvert)
                    else:
                        for element in trashNextPickupItem:
                            if element['value'] == item['date']:
                                __gen_json(item['nameType'], dateConvert)

                if name not in trashType:
                    if item['date'] >= self.date_today:
                        trash = {}
                        trashType[name] = item["nameType"]
                        trash['key'] = item['nameType']
                        trash['value'] = dateConvert
                        trash['days_remaining'] = (days(self.date_today, item['date']))
                        trashScheduleFull.append(trash)

                    if item['date'] > self.date_today:
                        if len(trashNextDays) == 0:
                            trashType[name] = "firts_next_in_days"
                            trashNextDays['key'] = "first_next_in_days"
                            trashNextDays['value'] = (days(self.date_today, item['date']))
                            trashFirstNextInDays.append(trashNextDays)

                    if item['date'] == self.date_today:
                        trashType['today'] = "today"
                        trashToday['key'] = "today"
                        trashScheduleToday.append(trashToday)
                        multiTrashToday.append(item['nameType'])
                        if len(multiTrashToday) != 0:
                            trashToday['value'] = ', '.join(multiTrashToday)

                    if item['date'] == self.date_tomorrow:
                        trashType[name] = "tomorrow"
                        trashTomorrow['key'] = "tomorrow"
                        trashScheduleTomorrow.append(trashTomorrow)
                        multiTrashTomorrow.append(item['nameType'])
                        if len(multiTrashTomorrow) != 0:
                            trashTomorrow['value'] = ', '.join(multiTrashTomorrow)

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

        return trashScheduleFull, trashScheduleToday, trashScheduleTomorrow, trashNextPickupItem, trashFirstNextInDays

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
    def trash_schedule_next_item_json(self):
        """Return both the pickup date and the container type."""
        return self._trashNextPickupItem

    @property
    def trash_type_list(self):
        """Return both the pickup date and the container type."""
        return self._trashTypes

trash = Afvaldienst('mijnafvalwijzer', '5146EG', '6', '')
print("\n")
print(trash.trash_schedulefull_json)
print("\n")
print(trash.trash_schedule_next_days_json)
print("\n")
print(trash.trash_schedule_today_json)
print("\n")
print(trash.trash_schedule_tomorrow_json)
print("\n")
print(trash.trash_schedule_next_item_json)
print("\n")
print(trash.trash_type_list)
