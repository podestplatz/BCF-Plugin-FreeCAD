class Identifiable:

    def __init__(self, id = None):
        self.id = id
        if not id:
            self.id = id(self)
