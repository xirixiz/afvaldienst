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
    >>> trash = Afval(provider, zipcode, housenumber, suffix)

    >>> trash.trash_raw_json
    [{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}, {'nameType': 'pmd', 'type': 'pmd', 'date': '2019-12-28'}]

    >>> trash.trash_next_json
    [{'nameType': 'gft', 'type': 'gft', 'date': '2019-12-20'}

    >>> trash.trash_type_list
    ['gft', 'kerstbomen', 'pmd', 'restafval', 'papier']


Contributors are most welcome
-----------------------------
* I'm still learning how to code properly. But a special thanks to Bart Dorlandt (https://github.com/bambam82/afvalwijzer) as I used his repository as base for this library.



