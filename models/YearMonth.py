#! /usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "Yifan Gu <YFGu0618@outlook.com>"


class YearMonth:
    """The Year-Month class

    For dealing with date with format 'YYYY-MM'
    """

    def __init__(self, start, end):
        """Initialize an object with predefined start time and end time

        Args:
            start (str): Start time of the iterator, in format of "YYYY-MM".
            end (str): End time of the iterator, in format of "YYYY-MM".
        """
        self._start_yr, self._start_mon = (int(x) for x in start.split('-', 2))
        self._end_yr, self._end_mon = (int(x) for x in end.split('-', 2))
        if self._start_mon == 1:
            self._yr, self._mon = self._start_yr - 1, 12
        else:
            self._yr, self._mon = self._start_yr, self._start_mon - 1

    def next(self):
        """Return the next month in format of "YYYY-MM"

        Returns:
            None, None: if the next month is beyond the range defined by "end".
            int, int: if there is a valid (year, month) to return.
        """
        if self._yr == self._end_yr:
            if self._mon < self._end_mon:
                self._mon += 1
            else:
                return None, None
        else:
            if self._mon == 12:
                self._yr += 1
                self._mon = 1
            else:
                self._mon += 1
        return self._yr, self._mon
