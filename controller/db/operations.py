import pymysql
import time

flag = False


class DBBroker:

    def __init__(self):
        global flag
        if flag is False:
            self.conn = pymysql.connect(host="localhost", user="root", passwd="", db="human_driving_res")
            flag = True

    def insert(self, result):
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        # omogucava upite
        myCursor = self.conn.cursor()

        myCursor.execute("INSERT INTO results(result,date) VALUES(%s, %s)", (result, now))

        self.conn.commit()
        self.conn.close()
        global flag
        flag = False

    def getAll(self):
        myCursor = self.conn.cursor()

        return myCursor

    def delete(self, id):
        myCursor = self.conn.cursor()

        myCursor.execute('DELETE FROM results WHERE id = {0}'.format(id))
        self.conn.commit()
        self.conn.close()
        global flag
        flag = False
