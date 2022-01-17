from db.operations import DBBroker

instance = DBBroker()


def insert(result):
    instance.insert(result)


def getAll():
    myCursor = instance.getAll()
    return myCursor


def delete(id):
    instance.delete(id)
