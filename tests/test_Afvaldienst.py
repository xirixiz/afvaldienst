import pytest
from Afvaldienst import Afvaldienst

class TestAfvaldienst(object):
    def test_provider(self):
        trash = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')
        assert trash.provider == 'mijnafvalwijzer'

    def test_zipcode(self):
        trash = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')
        assert trash.zipcode == '3825AL'

    def test_incorrect_zipcode(self):
        with pytest.raises(ValueError) as e:
            _ = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')

    def test_housenumber(self):
        trash = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')
        assert trash.housenumber == 41

    def test_housenumber_string(self):
        trash = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')
        assert trash.housenumber == '41'

    def test_suffix(self):
        trash = Afvaldienst('mijnafvalwijzer','3825AL', '41', '')
        assert trash.housenumber == ''
