# -*- coding: utf-8 -*-
"""Exceptions for Afvalwijzer and Afvalstoffendienst."""


class AfvaldienstError(Exception):
    """Generic Afvalwijzer and Afvalstoffendienst exception."""

    pass


class AfvaldienstConnectionError(TwenteMilieuError):
    """Afvalwijzer and Afvalstoffendienst connection exception."""

    pass


class AfvaldienstAddressError(TwenteMilieuError):
    """Afvalwijzer and Afvalstoffendienst unknown address exception."""

    pass
