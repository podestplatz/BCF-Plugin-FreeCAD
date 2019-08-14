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

from uuid import UUID

class Identifiable:

    """
    This class supplies every object, that inherits it, with a unique id. This
    id shall not be changed during runtime and is only set at object creation.
    """

    def __init__(self):
        self.id = id(self)


    def searchObject(self, object):

        """ Search for a member whose id == object.id

        Check whether `self.id == object.id` and return self.
        If this is not the case check every instance member.
        """

        pass


class XMLIdentifiable:

    """
    Holds the id the inheriting class should hold according to the xml file.
    This id is intended to be of type: UUID. Although it can also be a string,
    which, however, must be parsable as GUID for UUID.
    """

    def __init__(self, uId = UUID):
        if not uId:
            raise ValueError("XMLId may not be `None`")

        if isinstance(uId, str):
            try:
                self._id = UUID(uId)
            except Exception as e:
                self._raiseParseException(e)
        elif isinstance(uId, UUID):
            self._id = uId

    @property
    def xmlId(self):
        return self._id

    @xmlId.setter
    def xmlId(self, newVal):
        if isinstance(newVal, UUID):
            self._id = newVal
        elif isinstance(newVal, str):
            try:
                self._id = UUID(newVal)
            except Exception as e:
                self._raiseParseException(e)
        else:
            raise ValueError("Id has to be of type UUID or string!")


    def idEquals(self, otherId):

        if otherId is None:
            return False

        if type(self.xmlId) != type(otherId):
            return False

        return self.xmlId == otherId


    def _raiseParseException(self, exc):
        raise ValueError("Id could not be parsed as Guid from UUID."\
                "Error: {}".format(str(exc)))
