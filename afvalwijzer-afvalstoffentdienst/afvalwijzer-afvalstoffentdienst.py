# -*- coding: utf-8 -*-
"""Asynchronous Python client for the Afvalwijzer and Afvalstoffendienst API."""
import asyncio
import json
import socket
from datetime import date, datetime, timedelta
from typing import Dict, Optional

import re
import requests


import aiohttp
import async_timeout
from yarl import URL

from .__version__ import __version__
from .exceptions import (
    AfvaldienstAddressError,
    AfvaldienstConnectionError,
    AfvaldienstError,
)


class Afvaldienst(object):

    async def _request(self, uri: str, method: str = "POST", data=None):
        """Handle a request to Twente Milieu."""

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



        url = URL.build(
            scheme="https", host=API_HOST, port=443, path=API_BASE_URI
        ).join(URL(uri))

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        try:
            with async_timeout.timeout(self.request_timeout):
                response = await self._session.request(
                    method, url, data=data, headers=headers, ssl=True
                )
        except asyncio.TimeoutError as exception:
            raise TwenteMilieuConnectionError(
                "Timeout occurred while connecting to Twente Milieu API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise TwenteMilieuConnectionError(
                "Error occurred while communicating with Twente Milieu."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if (response.status // 100) in [4, 5]:
            contents = await response.read()
            response.close()

            if content_type == "application/json":
                raise TwenteMilieuError(
                    response.status, json.loads(contents.decode("utf8"))
                )
            raise TwenteMilieuError(
                response.status, {"message": contents.decode("utf8")}
            )

        if "application/json" in response.headers["Content-Type"]:
            return await response.json()
        return await response.text()




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
                    trash['key'] = name
                    trash['value'] = date
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