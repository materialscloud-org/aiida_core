# -*- coding: utf-8 -*-

import pytz
from datetime import datetime

from aiida import settings
from aiida.orm import Node


def get_dblogger_extra(obj):
    """
    Given an object (Node, Calculation, ...) return a dictionary to be passed
    as extra to the aiidalogger in order to store the exception also in the DB.
    If no such extra is passed, the exception is only logged on file.
    """

    if isinstance(obj, Node):
        if obj._plugin_type_string:
            objname = "node." + obj._plugin_type_string
        else:
            objname = "node"
    else:
        objname = obj.__class__.__module__ + "." + obj.__class__.__name__
    objpk = obj.pk
    return {'objpk': objpk, 'objname': objname}


# All the timezone part here is taken from Django.
# TODO SP: check license terms ?
# TODO SP: docstring
utc = pytz.utc


def get_default_timezone():
    return pytz.timezone(settings.TIME_ZONE)

get_current_timezone = get_default_timezone


def now():
    if getattr(settings, "USE_TZ", None):
        return datetime.utcnow().replace(tzinfo=utc)
    else:
        return datetime.now()


def is_naive(value):
    return value.utcoffset() is None


def is_aware(value):
    return value.utcoffset() is not None


def make_aware(value, timezone=None, is_dst=None):
    if timezone is None:
        timezone = get_current_timezone()
    if hasattr(timezone, 'localize'):
        return timezone.localize(value, is_dst=is_dst)
    else:
        if is_aware(value):
            raise ValueError(
                "make_aware expects a naive datetime, got %s" % value)
        # This may be wrong around DST changes!
        return value.replace(tzinfo=timezone)


def localtime(value, timezone=None):
    """
    Converts an aware datetime.datetime to local time.
    Local time is defined by the current time zone, unless another time zone
    is specified.
    """
    if timezone is None:
        timezone = get_current_timezone()
    # If `value` is naive, astimezone() will raise a ValueError,
    # so we don't need to perform a redundant check.
    value = value.astimezone(timezone)
    if hasattr(timezone, 'normalize'):
        # This method is available for pytz time zones.
        value = timezone.normalize(value)
    return value
