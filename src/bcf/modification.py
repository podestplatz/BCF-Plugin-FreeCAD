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
