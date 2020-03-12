import datetime
from collections import OrderedDict


def decode_date(string):
    """Decodes a date from a command line argument, returning datetime object".

    Args:
      string: See AssetSetCommand class comment for the allowable
        date formats.v

    Returns:
      long, datetime object
    Raises:
      ValueError: if string does not conform to a legal date format.
    """
    date_formats = ['%Y%m%d',
                    '%Y-%m-%d',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f']
    for date_format in date_formats:
        try:
            dt = datetime.datetime.strptime(string, date_format)
            return dt
        except ValueError:
            continue
    raise ValueError('Invalid format for date: "%s".' % string)
