from db.operations import DB


class Controller:
    def __init__(self):
        self.db = DB

    def insert(self, result):
        self.db.insert(result)

    def getAll(self):
        myCursor = self.db.getAll()
        return myCursor

    def delete(self, id):
        self.db.delete(id)
