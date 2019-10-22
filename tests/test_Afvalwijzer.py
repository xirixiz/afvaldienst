import pytest
from Afvaldienst import Afvaldienst

class TestAfvaldienst(object):
    def test_provider(self):
        trash = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')
        assert trash.provider == 'mijnafvalwijzer'

    def test_zipcode(self):
        trash = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')
        assert trash.zipcode == '1111AA'

    def test_incorrect_zipcode(self):
        with pytest.raises(ValueError) as e:
            _ = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')

    def test_housenumber(self):
        trash = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')
        assert trash.housenumber == 11

    def test_housenumber_string(self):
        trash = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')
        assert trash.housenumber == '11'

    def test_suffix(self):
        trash = Afvaldienst('mijnafvalwijzer','1111AA', '11', 'A')
        assert trash.housenumber == 'A'
