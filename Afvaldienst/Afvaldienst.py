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
            raise ValueError("Zipcode has a incorrect format. Example: 3564KV")

        _providers = ('mijnafvalwijzer', 'afvalstoffendienstkalender')
        if self.provider not in _providers:
            raise ValueError("Invalid provider: {}, please verify".format(self.provider))

        self.date_today = datetime.today().strftime('%Y-%m-%d')
        self.date_today = '2020-02-14'
        today_to_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=1)
        self.date_tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')
        day_after_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=2)
        self.date_dat = datetime.strftime(day_after_tomorrow, '%Y-%m-%d')

        self._jsonData = self.__get_data_json()
        self._trashTypes = self.__get_data_trash_types()
        self._trashScheduleFull, self._trashScheduleToday, self._trashScheduleTomorrow, self._trashScheduleDAT, self._trashNextPickupItem, self._trashNextPickupDate, self._trashFirstNextInDays = self.__get_trashschedule()

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
        trashDAT = {}
        multiTrashToday = []
        multiTrashTomorrow = []
        multiTrashDAT = []
        trashScheduleToday = []
        trashScheduleTomorrow = []
        trashScheduleDAT = []
        trashScheduleFull = []
        multiTrashNextPickupItem = []
        trashNextPickupItem = []
        trashNextPickupDate = []
        trashFirstNextInDays = []
        trashTypesExtended = ['today', 'tomorrow', 'next']
        trashTypesExtended.extend(self._trashTypes)

        if self.countToday == 'yes':
            countToday = self.date_today
        else:
            countToday = self.date_tomorrow

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
                    global trash_json
                    trash_json = {}
                    trash_json['key'] = name
                    trash_json['value'] = date
                    return trash_json

                if item['date'] >= countToday:
                    if len(trashNextPickupItem) == 0:
                        __gen_json('first_next_item', item['nameType'])
                        dateChecker = item['date']
                        trashNextPickupItem.append(trash_json)
                        multiTrashNextPickupItem.append(item['nameType'])
                    else:
                        for element in trashNextPickupItem:
                             if dateChecker == item['date']:
                                element['value'] = ', '.join(multiTrashNextPickupItem).strip()

                    if len(trashNextPickupDate) == 0:
                        __gen_json('first_next_date', dateConvert)
                        trashNextPickupDate.append(trash_json)

                if name not in trashType:
                    if item['date'] >= self.date_today:
                        trash = {}
                        trashType[name] = item["nameType"]
                        trash['key'] = item['nameType']
                        trash['value'] = dateConvert
                        trash['days_remaining'] = (days(self.date_today, item['date']))
                        trashScheduleFull.append(trash)

                    if item['date'] >= countToday:
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

                    if item['date'] == self.date_dat:
                        trashType[name] = "day_after_tomorrow"
                        trashDAT['key'] = "day_after_tomorrow"
                        trashScheduleDAT.append(trashDAT)
                        multiTrashDAT.append(item['nameType'])
                        if len(multiTrashDAT) != 0:
                            trashDAT['value'] = ', '.join(multiTrashDAT)

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