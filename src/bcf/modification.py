from datetime import datetime

class Modification:

    """
    This class is used by Topic and Comment to for one denote the author
    and date of the last change and the creator and the creation date of an
    object of one of the respective classes
    """

    def __init__(self,
            author: str,
            date: datetime):

        """ Initialisation function for Modification """

        self.author = author
        self.date = date


    def __eq__(self, other):

        """
        Returns true if every variable member of both classes are the same
        """

        return self.author == other.author and self.date == other.date
