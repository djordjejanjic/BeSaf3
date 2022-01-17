from db.operations import DBBroker


def insert(result):
    DBBroker.insert(result)


def getAll():
    myCursor = DBBroker.getAll()
    return myCursor


def delete(id):
    DBBroker.delete(id)
