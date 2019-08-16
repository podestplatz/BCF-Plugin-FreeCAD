"""
Copyright (C) 2019 PODEST Patrick

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

"""
Author: Patrick Podest
Date: 2019-08-16
Github: @podestplatz

**** Description ****
This file just provides a filter for the logging framework of python, that
filters out every validation error message that should be printed to Stdout.
"""

from logging import Filter

class StdoutFilter(Filter):

    """ This filter filters out all error messages created orginally by the
    xmlschema library. """

    def __init__(self, name=""):

        Filter.__init__(self, name)


    def filter(self, record):

        msg = record.getMessage()
        requiredWords = ["Reason", "Instance", "Schema", "Path"]

        log = 0
        for word in requiredWords:
            if word not in msg:
                log = 1

        return log
