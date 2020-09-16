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
from collections import defaultdict
from datetime import date, datetime, timedelta

class Afvaldienst(object):
    def __init__(self, provider, api_token, zipcode, housenumber, suffix, start_date, label):
        self.provider = provider
        self.api_token = api_token
        self.housenumber = housenumber
        self.suffix = suffix
        self.start_date = start_date
        self.label_none = label

        _zipcode = re.match('^\d{4}[a-zA-Z]{2}', zipcode)

        if _zipcode:
            self.zipcode = _zipcode.group()
        else:
            print("Zipcode has a incorrect format. Example: 1111AA")

        _providers = ('mijnafvalwijzer', 'afvalstoffendienstkalender')
        if self.provider not in _providers:
            print("Invalid provider: {}, please verify".format(self.provider))

        if not self.api_token:
            print("The API key has not been specified, please verify.")

        self.date_today = datetime.today().strftime('%Y-%m-%d')
        today_to_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=1)
        self.date_tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')
        day_after_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=2)
        self.date_day_after_tomorrow = datetime.strftime(day_after_tomorrow, '%Y-%m-%d')

        self._trash_json = self.__get_json()
        self._trash_types = self.__get_trash_types()
        self._trash_schedule, self._trash_schedule_custom = self.__get_trash_schedule()
        self._trash_types_from_schedule = self.__get_trash_types_from_schedule()

    def __get_json(self):
        url = 'https://api.{}.nl/webservices/appsinput/?apikey={}&method=postcodecheck&postcode={}&street=&huisnummer={}&toevoeging={}&app_name=afvalwijzer&platform=phone&afvaldata={}&langs=nl'.format(self.provider, self.api_token, self.zipcode, int(self.housenumber), self.suffix, self.date_today)

        try:
            raw_response = requests.get(url)
        except requests.exceptions.RequestException as err:
            raise ValueError(err)
            raise ValueError('Provider URL not reachable or a different error appeared. Please verify the url:' + url + 'manually in your browser. Text mixed with JSON should be visible.')

        try:
            json_response = raw_response.json()
        except ValueError:
            raise ValueError('No JSON data received from ' + url)

        try:
            json_data = (json_response['ophaaldagen']['data'] + json_response['ophaaldagenNext']['data'])
            return json_data
        except ValueError:
            raise ValueError('Invalid JSON data received from ' + url)

    # Function: create a list of all trash types within the json response
    def __get_trash_types(self):
        trash_types = list()
        for x in self._trash_json:
            trash_type = x["nameType"].strip()
            if trash_type not in trash_types:
                trash_types.append(trash_type)
        return trash_types

    # Function: create a list of all trash types from trash_schedule and trash_schedule_custom
    def __get_trash_types_from_schedule(self):
        trash_types_from_schedule = list()
        for x in self.trash_schedule + self.trash_schedule_custom:
            trash_type = x["key"].strip()
            if trash_type not in trash_types_from_schedule:
                trash_types_from_schedule.append(trash_type)
        return trash_types_from_schedule

    # Function: calculate amount of days between two dates
    def __calculate_days_between_dates(self, start, end):
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        return (abs((end_date-start_date).days))

    # Function: json/dict generator
    def __gen_json(self, key, value, **kwargs):
        global gen_json
        gen_json = dict()
        gen_json['key'] = key
        gen_json['value'] = value
        if kwargs:
            gen_json['days_remaining'] = kwargs.get('days_remaining', self.label_none)
        return gen_json

    # Function: trash_schedule and trash_schedule_custom generator
    def __get_trash_schedule(self):
        trash_schedule = list()
        trash_schedule_custom = list()
        temp_dict = dict()
        temp_list_today = list()
        temp_list_tomorrow = list()
        temp_list_day_after_tomorrow = list()
        temp_list_first_next_item = list()

        # Start counting wihth Today's date or with Tomorrow's date
        if self.start_date.casefold() in ('true', 'yes'):
            start_date = self.date_today
        else:
            start_date = self.date_tomorrow

        for json in self._trash_json:
            trash_name = json['nameType'].strip()
            trash_date = json['date']
            trash_date_custom_format = datetime.strptime(json['date'], '%Y-%m-%d').strftime('%d-%m-%Y')

            # Append trash names and pickup dates
            if not any(x['key'] == trash_name for x in trash_schedule):
                if trash_date >= self.date_today:
                    self.__gen_json(trash_name, trash_date_custom_format, days_remaining=(self.__calculate_days_between_dates(self.date_today, trash_date)))
                    trash_schedule.append(gen_json)

            # Append key with value none if key not found
            if not any(x['key'] == 'today' for x in trash_schedule_custom):
                self.__gen_json('today', self.label_none)
                trash_schedule_custom.append(gen_json)
            if not any(x['key'] == 'tomorrow' for x in trash_schedule_custom):
                self.__gen_json('tomorrow', self.label_none)
                trash_schedule_custom.append(gen_json)
            if not any(x['key'] == 'day_after_tomorrow' for x in trash_schedule_custom):
                self.__gen_json('day_after_tomorrow', self.label_none)
                trash_schedule_custom.append(gen_json)

            # Append today's (multiple) trash items
            if trash_date == self.date_today:
                if any(x['key'] == 'today' for x in trash_schedule_custom):
                    temp_list_today.append(trash_name)
                    for dictionary in trash_schedule_custom:
                        if dictionary['key'] == 'today':
                            dictionary['value'] = ', '.join(temp_list_today)
                else:
                    self.__gen_json('today', trash_name)
                    trash_schedule_custom.append(gen_json)

            # Append tomorrow's (multiple) trash items
            if trash_date == self.date_tomorrow:
                if any(x['key'] == 'tomorrow' for x in trash_schedule_custom):
                    temp_list_tomorrow.append(trash_name)
                    for dictionary in trash_schedule_custom:
                        if dictionary['key'] == 'tomorrow':
                            dictionary['value'] = ', '.join(temp_list_tomorrow)
                else:
                    self.__gen_json('tomorrow', trash_name)
                    trash_schedule_custom.append(gen_json)

            # # Append day_after_tomorrow's (multiple) trash items
            if trash_date == self.date_day_after_tomorrow:
                if any(x['key'] == 'day_after_tomorrow' for x in trash_schedule_custom):
                    temp_list_day_after_tomorrow.append(trash_name)
                    for dictionary in trash_schedule_custom:
                        if dictionary['key'] == 'day_after_tomorrow':
                            dictionary['value'] = ', '.join(temp_list_day_after_tomorrow)
                else:
                    self.__gen_json('day_after_tomorrow', trash_name)
                    trash_schedule_custom.append(gen_json)

            if trash_date >= start_date:
                # Append days until next pickup
                if not any(x['key'] == 'first_next_in_days' for x in trash_schedule_custom):
                    self.__gen_json("first_next_in_days", (self.__calculate_days_between_dates(self.date_today, trash_date)))
                    trash_schedule_custom.append(gen_json)

                # Append the first upcoming (multiple) trash name(s) to be picked up
                if not any(x['key'] == 'first_next_item' for x in trash_schedule_custom):
                    self.__gen_json("first_next_item", trash_name)
                    trash_schedule_custom.append(gen_json)
                    dateCheck = trash_date
                if any(x['key'] == 'first_next_item' for x in trash_schedule_custom):
                    if trash_date == dateCheck:
                        temp_list_first_next_item.append(trash_name)
                        for dictionary in trash_schedule_custom:
                            if dictionary['key'] == 'first_next_item':
                                dictionary['value'] = ', '.join(temp_list_first_next_item)

                # Append first upcoming date for next pickup
                if not any(x['key'] == 'first_next_date' for x in trash_schedule_custom):
                    self.__gen_json("first_next_date", trash_date_custom_format)
                    trash_schedule_custom.append(gen_json)

        # Append all trash types from the current year
        for trash_name in self._trash_types:
            if not any(x['key'] == trash_name for x in trash_schedule):
                self.__gen_json(trash_name, self.label_none, days_remaining=self.label_none)
                trash_schedule.append(gen_json)

        return trash_schedule, trash_schedule_custom

    @property
    def trash_json(self):
        """Return both the pickup date and the container type."""
        return self._trash_json

    @property
    def trash_schedule(self):
        """Return both the pickup date and the container type from the provider."""
        return self._trash_schedule

    @property
    def trash_schedule_custom(self):
        """Return a custom list of added trash pickup information."""
        return self._trash_schedule_custom

    @property
    def trash_types_from_schedule(self):
        """Return all available trash types from the provider."""
        return self._trash_types_from_schedule

    @property
    def trash_types(self):
        """Return all available trash types from the provider."""
        return self._trash_types
