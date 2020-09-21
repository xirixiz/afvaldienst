Afvaldienst library
===================

This library is meant to interface with mijnafvalwijzer.nl and/or afvalstoffendienstkalender.nl
It is meant to use with home automation projects like Home Assistant.


Installation
------------

.. code:: bash

    pip install afvaldienst


Uninstallation
--------------

.. code:: bash

    pip uninstall afvaldienst


Usage
-----

.. code:: python

    >>> from Afvaldienst import Afvaldienst
    >>> provider = 'mijnafvalwijzer'
    >>> api_token = ''
    >>> zipcode = '1111AA'
    >>> housenumber = '1'
    >>> suffix = ''
    >>> start_date = 'True or False'     (start counting wihth Today's date or with Tomorrow's date)
    >>> trash = Afvaldienst(provider, api_token, zipcode, housenumber, suffix)

    >>> trash.trash_json
    [{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}, {'nameType': 'pmd', 'type': 'pmd', 'date': '2019-12-28'}]

    >>> trash.trash_schedule
    [{'key': 'pmd', 'value': '31-10-2019', 'days_remaining': 8}, {'key': 'restafval', 'value': '15-11-2019', 'days_remaining': 23}, {'key': 'papier', 'value': '20-11-2019', 'days_remaining': 28}]

    >>> trash.trash_schedule_custom
    [{'key': 'first_next_in_days', 'value': 8}, {'key': 'today', 'value': 'None'}, {'key': 'tomorrow', 'value': 'None'},

    >>> trash.trash_types
    ['gft', 'kerstbomen', 'pmd', 'restafval', 'papier']


Or use the scraper:

    >>>from AfvaldienstScraper import AfvaldienstScraper
    >>> provider = 'mijnafvalwijzer'
    >>> zipcode = '1111AA'
    >>> housenumber = '1'
    >>> start_date = 'True or False'     (start counting wihth Today's date or with Tomorrow's date)
    >>> trash = AfvaldienstScraper(provider, zipcode, housenumber)

    >>> trash.trash_schedule
    [{'key': 'pmd', 'value': '31-10-2019', 'days_remaining': 8}, {'key': 'restafval', 'value': '15-11-2019', 'days_remaining': 23}, {'key': 'papier', 'value': '20-11-2019', 'days_remaining': 28}]

    >>> trash.trash_schedule_custom
    [{'key': 'first_next_in_days', 'value': 8}, {'key': 'today', 'value': 'None'}, {'key': 'tomorrow', 'value': 'None'},

    >>> trash.trash_types
    ['gft', 'kerstbomen', 'pmd', 'textiel', 'restafval', 'papier']

    >>>> trash.trash_types_from_schedule
    ['gft', 'papier', 'pmd', 'restafval', 'textiel', 'kerstbomen', 'today', 'tomorrow', 'day_after_tomorrow', 'first_next_in_days', 'first_next_item', 'first_next_date']


Contributors are most welcome
-----------------------------
* I'm still learning how to code properly.
