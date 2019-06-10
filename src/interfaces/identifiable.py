class Identifiable:

    def __init__(self, uId = None):
        self.id = uId
        if not id:
            self.id = id(self)
