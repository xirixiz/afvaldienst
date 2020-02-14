#!/usr/bin/env python3

from Afvaldienst import Afvaldienst

trash = Afvaldienst('mijnafvalwijzer', '5146EG', '6', '', 'true')
print("\n")
print(trash.trash_schedulefull_json)
print("\n")
print(trash.trash_schedule_next_days_json)
print("\n")
print(trash.trash_schedule_today_json)
print("\n")
print(trash.trash_schedule_tomorrow_json)
print("\n")
print(trash.trash_schedule_dat_json)
print("\n")
print(trash.trash_schedule_next_item_json)
print("\n")
print(trash.trash_schedule_next_date_json)
print("\n")
print(trash.trash_type_list)