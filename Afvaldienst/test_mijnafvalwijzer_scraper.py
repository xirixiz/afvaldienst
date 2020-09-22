#!/usr/bin/env python3

from AfvaldienstScraper import AfvaldienstScraper

#trash = AfvaldienstScraper('mijnafvalwijzer', '5146EG', '2', 'false', 'Geen')
#trash = AfvaldienstScraper('mijnafvalwijzer', '6851GJ', '2', 'false', 'Geen')
#trash = AfvaldienstScraper('mijnafvalwijzer', '3911CX', '178', 'false', 'Geen')
#trash = AfvaldienstScraper('mijnafvalwijzer', '1906KD', '17', 'false', 'Geen')
#trash = AfvaldienstScraper('mijnafvalwijzer', '3863AT', '27', 'false', 'Geen')
trash = AfvaldienstScraper('mijnafvalwijzer', '5018EH', '1', 'false', 'Geen')

#print(trash.trash_raw_json)
#print("\n")
# print(trash.trash_data)
# print("\n")
print(trash.trash_schedule)
print("\n")
print(trash.trash_schedule_custom)
print("\n")
print(trash.trash_types)
print("\n")
print(trash.trash_types_from_schedule)
print("\n")

# print(trash.trash_json)
# print("\n")

# TEST_DATA
# self.date_today = '2020-09-17'
# json_data = [{"nameType":"gft","type":"gft","date":"2020-01-03"},{"nameType":"pmd","type":"pmd","date":"2020-01-09"},{"nameType":"restafval","type":"restafval","date":"2020-01-10"},{"nameType":"kerstbomen","type":"kerstbomen","date":"2020-01-11"},{"nameType":"restafval","type":"restafval","date":"2020-07-24"},{"nameType":"gft","type":"gft","date":"2020-07-31"},{"nameType":"pmd","type":"pmd","date":"2020-08-06"},{"nameType":"gft","type":"gft","date":"2020-08-14"},{"nameType":"papier","type":"papier","date":"2020-08-19"},{"nameType":"pmd","type":"pmd","date":"2020-08-20"},{"nameType":"restafval","type":"restafval","date":"2020-08-21"},{"nameType":"gft","type":"gft","date":"2020-08-28"},{"nameType":"pmd","type":"pmd","date":"2020-09-03"},{"nameType":"gft","type":"gft","date":"2020-09-11"},{"nameType":"papier","type":"papier","date":"2020-09-17"},{"nameType":"pmd","type":"pmd","date":"2020-09-17"},{"nameType":"restafval","type":"restafval","date":"2020-09-18"},{"nameType":"gft","type":"gft","date":"2020-09-25"},{"nameType":"pmd","type":"pmd","date":"2020-10-01"},{"nameType":"gft","type":"gft","date":"2020-10-09"},{"nameType":"pmd","type":"pmd","date":"2020-10-15"},{"nameType":"restafval","type":"restafval","date":"2020-10-16"},{"nameType":"papier","type":"papier","date":"2020-10-21"},{"nameType":"gft","type":"gft","date":"2020-10-23"},{"nameType":"pmd","type":"pmd","date":"2020-10-29"},{"nameType":"gft","type":"gft","date":"2020-11-06"},{"nameType":"pmd","type":"pmd","date":"2020-11-12"},{"nameType":"restafval","type":"restafval","date":"2020-11-13"},{"nameType":"papier","type":"papier","date":"2020-11-18"},{"nameType":"gft","type":"gft","date":"2020-11-20"},{"nameType":"pmd","type":"pmd","date":"2020-11-26"},{"nameType":"gft","type":"gft","date":"2020-12-04"},{"nameType":"pmd","type":"pmd","date":"2020-12-10"},{"nameType":"restafval","type":"restafval","date":"2020-12-11"},{"nameType":"papier","type":"papier","date":"2020-12-16"},{"nameType":"gft","type":"gft","date":"2020-12-18"},{"nameType":"pmd","type":"pmd","date":"2020-12-24"}]
