from uuid import UUID

class Identifiable:

    """
    Provides a member id to the inheriting class. This id is intended to be of
    two types: UUID and str.
    """

    def __init__(self, uId = None):
        self._id = uId
        if not id:
            self._id = id(self)

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
            except:
                self._id = newVal
        else:
            raise ValueError("Id has to be of type UUID or string!")


    def idEquals(self, otherId):

        if otherId is None:
            return False

        if type(self.id) != type(otherId):
            return False

        return self.id == otherId
