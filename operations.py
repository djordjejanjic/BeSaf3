import pymysql
import time


def insert(result):
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    conn = pymysql.connect(host="localhost", user="root", passwd="", db="human_driving_res")

    # omogucava upite
    myCursor = conn.cursor()

    myCursor.execute("INSERT INTO results(result,date) VALUES(%s, %s)", (result, now))

    conn.commit()
    conn.close()


def getAll():
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="human_driving_res")

    myCursor = conn.cursor()

    return myCursor


def delete(id):
    conn = pymysql.connect(host="localhost", user="root", passwd="", db="human_driving_res")
    myCursor = conn.cursor()

    myCursor.execute('DELETE FROM results WHERE id = {0}'.format(id))
    conn.commit()
