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
    >>> zipcode = '3825AL'
    >>> housenumber = '41'
    >>> suffix = ''
    >>> trash = Afvaldienst(provider, zipcode, housenumber, suffix)

    >>> trash.trash_raw_json
    [{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}, {'nameType': 'pmd', 'type': 'pmd', 'date': '2019-12-28'}]

    >>> trash.trash_schedulefull_json
    [{'key': 'pmd', 'value': '31-10-2019', 'days_remaining': 8}, {'key': 'restafval', 'value': '15-11-2019', 'days_remaining': 23}, {'key': 'papier', 'value': '20-11-2019', 'days_remaining': 28}]

    >>> trash.trash_schedule_next_days_json
    [{'key': 'first_next_in_days', 'value': 8}]

    >>> trash.trash_schedule_today_json
    [{'key': 'today', 'value': 'None'}]

    >>> trash.trash_schedule_tomorrow_json
    [{'key': 'tomorrow', 'value': 'None'}]

    >>> trash.trash_schedule_next_item_json
    [{'key': 'gft', 'value': '25-10-2019'}]

    >>> trash.trash_type_list
    ['gft', 'kerstbomen', 'pmd', 'restafval', 'papier']


Contributors are most welcome
-----------------------------
* I'm still learning how to code properly. But a special thanks to Bart Dorlandt (https://github.com/bambam82/afvalwijzer) as I used his repository as base for this library.



