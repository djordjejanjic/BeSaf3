from db.operations import DBBroker


class Controller:
    def __init__(self):
        self.db = DBBroker()

    def insert(self, result):
        self.db.insert(result)

    def getAll(self):
        myCursor = self.db.getAll()
        return myCursor

    def delete(self, id):
        self.db.delete(id)
