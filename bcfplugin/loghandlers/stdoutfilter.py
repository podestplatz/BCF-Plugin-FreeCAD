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
