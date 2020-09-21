#!/usr/bin/env python3

from AfvaldienstScraper import AfvaldienstScraper

trash = AfvaldienstScraper('afvalstoffendienstkalender', '5061DR', '120', 'false', 'Geen')
#trash = AfvaldienstScraper('mijnafvalwijzer', '5146EG', '2', 'false', 'Geen')

print(trash.trash_schedule)
print("\n")
print(trash.trash_schedule_custom)
print("\n")
print(trash.trash_types)
print("\n")
print(trash.trash_types_from_schedule)
print("\n")