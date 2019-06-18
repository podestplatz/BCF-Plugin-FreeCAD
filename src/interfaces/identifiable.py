from uuid import UUID

class Identifiable:

    """
    Provides a member id to the inheriting class. This id is intended to be
    of type: UUID. Although it can also be a string, which, however, must be
    parsable as GUID for UUID.
    """

    def __init__(self, uId = UUID):
        if not uId:
            raise ValueError("Id may not be `None`")

        if isinstance(uId, str):
            try:
                self._id = UUID(uId)
            except Exception as e:
                self._raiseParseException(e)
        elif isinstance(uId, UUID):
            self._id = uId

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, newVal):
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

        if type(self.id) != type(otherId):
            return False

        return self.id == otherId


    def _raiseParseException(self, exc):
        raise ValueError("Id could not be parsed as Guid from UUID."\
                "Error: {}".format(str(exc)))
