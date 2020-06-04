#!/usr/bin/env python3

from Afvaldienst import Afvaldienst

#trash = Afvaldienst('mijnafvalwijzer', '5146EG', '6', '', 'false')
#trash = Afvaldienst('mijnafvalwijzer', '6851GJ', '2', '', 'false')
#trash = Afvaldienst('mijnafvalwijzer', '3911CX', '178', '', 'false')
trash = Afvaldienst('mijnafvalwijzer', '1906KD', '17', '', 'false')

print(trash.trash_raw_json)

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
