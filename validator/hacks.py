'''
This module contains ugly hacks. It should serve as a reminder to actually
solve the underlying problems instead of using the hacks contained.
But what can you do?
'''
from pandas.core.frame import DataFrame
from pygeobase.object_base import TS

# import warnings

'''
Wrapper for data readers that discards timezone information from the data
on the fly - because pytesmo can't handle it.
Remove after https://github.com/TUW-GEO/pytesmo/issues/150 is fixed.
'''
class TimezoneAdapter(object):

    def __init__(self, reader):
        self.reader = reader

    def read_ts(self, *args, **kwargs):
        data = self.reader.read_ts(*args, **kwargs)

        if type(data) is TS or issubclass(type(data), TS):
            data = data.data

        if data.index.tz is not None:
#             warnings.warn('Dropping timezone information for data')
            data.index = data.index.tz_convert(None)
        return data

    def read(self, *args, **kwargs):
        data = self.reader.read(*args, **kwargs)

        if type(data) is TS or issubclass(type(data), TS):
            data = data.data

        if data.index.tz is not None:
#             warnings.warn('Dropping timezone information for data')
            data.index = data.index.tz_convert(None)
        return data
