# -*- coding: utf-8 -*-

"""
This library is meant to interface with mijnafvalwijzer.nl and/or afvalstoffendienstkalender.nl
It is meant to use with home automation projects like Home Assistant.

Author: Bram van Dartel (https://github.com/xirixiz/)

## Usage - see README.rst

"""
import re
import json
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
import urllib.request
import urllib.error

class AfvaldienstScraper(object):
    def __init__(self, provider, zipcode, housenumber, start_date, label):
        self.provider = provider
        self.housenumber = housenumber
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

        self.date_today = datetime.today().strftime('%Y-%m-%d')
        today_to_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=1)
        self.date_tomorrow = datetime.strftime(today_to_tomorrow, '%Y-%m-%d')
        day_after_tomorrow = datetime.strptime(self.date_today, '%Y-%m-%d') + timedelta(days=2)
        self.date_day_after_tomorrow = datetime.strftime(day_after_tomorrow, '%Y-%m-%d')

        # Start counting wihth Today's date or with Tomorrow's date
        if self.start_date.casefold() in ('true', 'yes'):
            self.date_selected = self.date_today
        else:
            self.date_selected = self.date_tomorrow

        self._trash_data, self._trash_data_custom = self.__get_data()
        self._trash_types = self.__get_trash_types()
        self._trash_schedule, self._trash_schedule_custom = self.__get_trash_schedule()
        self._trash_types_from_schedule = self.__get_trash_types_from_schedule()

    def get_date_from_afvaltype(self, html, afvaltype, afvalnaam):
        month_to_number = {
            "jan": "01",
            "feb": "02",
            "mrt": "03",
            "apr": "04",
            "mei": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "okt": "10",
            "nov": "11",
            "dec": "12",
            "januari": "01",
            "februari": "02",
            "maart": "03",
            "april": "04",
            "mei": "05",
            "juni": "06",
            "juli": "07",
            "augustus": "08",
            "september": "09",
            "oktober": "10",
            "november": "11",
            "december": "12",
        }

        try:
            results = html.findAll("p", {"class": afvaltype})

            for result in results:
                date = result.find("span", {"class": "span-line-break"})

                #Sometimes there is no span with class span-line-break
                #so we just get the result as date
                if date is None:
                    date = str(result).split(">")[1]
                    date = date.split("<")[0]
                else:
                    # get the value of the span
                    date = date.string

                day = date.split()[1]
                month = month_to_number[date.split()[2]]
                # the year is always this year because it's a 'jaaroverzicht'
                year = datetime.today().year

                if int(month) >= datetime.today().month:
                    if int(month) == datetime.today().month:
                        if int(day) >= datetime.today().day:
                            return str(year) + "-" + str(month) + "-" + str(day)
                    else:
                        return str(year) + "-" + str(month) + "-" + str(day)
            # if nothing was found
            return ''
        except Exception as exc:
            print("Something went wrong while splitting data: %r. This probably means that trash type %r is not supported on your location", exc, afvalnaam)
            return ''


    def __get_data(self):
        try:
            url = 'https://www.{0}.nl/nl/{1}/{2}/'.format(self.provider, self.zipcode, int(self.housenumber))
            req = urllib.request.Request(url=url)
            f = urllib.request.urlopen(req)
            html = f.read().decode("utf-8")

            soup = BeautifulSoup(html, "html.parser")
            jaaroverzicht = soup.find(id="jaaroverzicht")

            # Place all possible values in the dictionary even if they are not necessary
            waste_dict = {}
            waste_list = []

            # find gft.
            waste_dict["gft"] = self.get_date_from_afvaltype(jaaroverzicht, "gft", "gft")
            if len(waste_dict["gft"]) == 0:
                waste_dict["gft"] = self.get_date_from_afvaltype(jaaroverzicht, "restgft", "gft")
            # find papier
            waste_dict["papier"] = self.get_date_from_afvaltype(jaaroverzicht, "papier", "papier")
            if len(waste_dict["papier"]) == 0:
                waste_dict["papier"] = self.get_date_from_afvaltype(jaaroverzicht, "dhm", "papier")
            # find pmd.
            waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "pd", "pmd")
            if len(waste_dict["pmd"]) == 0:
                waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "pmd", "pmd")
            if len(waste_dict["pmd"]) == 0:
                waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "pbd", "pmd")
            if len(waste_dict["pmd"]) == 0:
                waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "plastic", "pmd")
            if len(waste_dict["pmd"]) == 0:
                waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "dhm", "pmd")
            if len(waste_dict["pmd"]) == 0:
                waste_dict["pmd"] = self.get_date_from_afvaltype(jaaroverzicht, "gkbp", "pmd")
            # find restafval.
            waste_dict["restafval"] = self.get_date_from_afvaltype(jaaroverzicht, "restafval", "restafval")
            if len(waste_dict["restafval"]) == 0:
                waste_dict["restafval"] = self.get_date_from_afvaltype(jaaroverzicht, "restgft", "restafval")
            # find luiers
            waste_dict["luiers"] = self.get_date_from_afvaltype(jaaroverzicht, "luiers", "luiers")
            # find kerstboom
            waste_dict["kerstbomen"] = self.get_date_from_afvaltype(jaaroverzicht, "kerstboom", "kerstbomen")

            # append custom sensors
            waste_dict_custom = {}
            waste_list_custom = []
            today_multiple_items = []
            tomorrow_multiple_items = []
            day_after_tomorrow_multiple_items = []
            first_next_item_multiple_items = []

            waste_dict_temp = {key:value for key,value in waste_dict.items() if len(value) != 0}

            for key,value in waste_dict_temp.items():
                if value == self.date_today:
                    if "today" in waste_dict_custom.keys():
                        today_multiple_items.append(key)
                        waste_dict_custom["today"] = ', '.join(today_multiple_items)
                    else:
                        today_multiple_items.append(key)
                        waste_dict_custom["today"] = key

                if value == self.date_tomorrow:
                    if "tomorrow" in waste_dict_custom.keys():
                        tomorrow_multiple_items.append(key)
                        waste_dict_custom["tomorrow"] = ', '.join(tomorrow_multiple_items)
                    else:
                        tomorrow_multiple_items.append(key)
                        waste_dict_custom["tomorrow"] = key

                if value == self.date_day_after_tomorrow:
                    if "day_after_tomorrow" in waste_dict_custom.keys():
                        day_after_tomorrow_multiple_items.append(key)
                        waste_dict_custom["day_after_tomorrow"] = ', '.join(day_after_tomorrow_multiple_items)
                    else:
                        day_after_tomorrow_multiple_items.append(key)
                        waste_dict_custom["day_after_tomorrow"] = key

            if "today" not in waste_dict_custom.keys():
                waste_dict_custom["today"] = self.label_none
            if "tomorrow" not in waste_dict_custom.keys():
                waste_dict_custom["tomorrow"] = self.label_none
            if "day_after_tomorrow" not in waste_dict_custom.keys():
                waste_dict_custom["day_after_tomorrow"] = self.label_none

            waste_dict_temp_date_selected = {key:value for key,value in waste_dict.items() if len(value) != 0 and value >= self.date_selected}

            first_date = min(waste_dict_temp_date_selected.values())
            waste_dict_custom["first_next_date"] = datetime.strptime(min(waste_dict_temp_date_selected.values()), '%Y-%m-%d').strftime('%d-%m-%Y')
            waste_dict_custom["first_next_in_days"] = self.__calculate_days_between_dates(self.date_today, min(waste_dict_temp_date_selected.values()))
            for key,value in waste_dict_temp_date_selected.items():
                if value == first_date:
                    if "first_next_item" in waste_dict_custom.keys():
                        first_next_item_multiple_items.append(key)
                        waste_dict_custom["first_next_item"] = ', '.join(first_next_item_multiple_items)
                    else:
                        first_next_item_multiple_items.append(key)
                        waste_dict_custom["first_next_item"] = key

            if "first_next_date" not in waste_dict_custom.keys():
                waste_dict_custom["first_next_date"] = self.label_none
            if "first_next_in_days" not in waste_dict_custom.keys():
                waste_dict_custom["first_next_in_days"] = self.label_none
            if "first_next_item" not in waste_dict_custom.keys():
                waste_dict_custom["first_next_item"] = self.label_none

            for key, value in waste_dict.items():
                self.__gen_json(key, value)
                waste_list.append(gen_json)

            for key, value in waste_dict_custom.items():
                self.__gen_json(key, value)
                waste_list_custom.append(gen_json)

            return waste_list, waste_list_custom
        except urllib.error.URLError as exc:
            print("Error occurred while fetching data: %r", exc.reason)
            return False

    # Function: create a list of all trash types within the json response
    def __get_trash_types(self):
        trash_types = list()
        for x in self._trash_data:
            trash_type = x["key"].strip()
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
        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")
        return (abs((end-start).days))

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

        # Append trash types from the provider with a valid date
        for json in self._trash_data:
            trash_name = json['key'].strip()
            trash_date = json['value']
            if len(json['value']) != 0:
                trash_date_custom_format = datetime.strptime(json['value'], '%Y-%m-%d').strftime('%d-%m-%Y')

                # Append trash names and pickup dates
                if not any(x['key'] == trash_name for x in trash_schedule):
                    if trash_date >= self.date_today:
                        self.__gen_json(trash_name, trash_date_custom_format, days_remaining=(self.__calculate_days_between_dates(self.date_today, trash_date)))
                        trash_schedule.append(gen_json)

        # Append custom trash sensors
        for json in self._trash_data_custom:
            key = json['key'].strip()
            value = json['value']
            if not any(x['key'] == key for x in trash_schedule_custom):
                self.__gen_json(key, value)
                trash_schedule_custom.append(gen_json)

        # Append all trash types from the from the provider from the current year if not in the list
        for trash_name in self._trash_types:
            if not any(x['key'] == trash_name for x in trash_schedule):
                self.__gen_json(trash_name, self.label_none, days_remaining=self.label_none)
                trash_schedule.append(gen_json)

        return trash_schedule, trash_schedule_custom

    @property
    def trash_data(self):
        """Return both the pickup date and the container type."""
        return self._trash_data, self._trash_data_custom

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
