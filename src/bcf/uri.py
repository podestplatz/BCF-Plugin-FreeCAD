"""
Wrapper class for a URI, maybe will get replaced by the uri module in the
future
"""
class Uri:
    def __init__(self, uri: str):
        self.uri = uri


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.uri == other.uri
