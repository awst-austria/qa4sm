import os
import sqlite3


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn


def update_task(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE tasks
              SET priority = ? ,
                  begin_date = ? ,
                  end_date = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()


if __name__ == '__main__':
    directory = r'../db.sqlite3'
    conn = None

    sql = ''' UPDATE validator_ismnnetworks
                  SET station_info = ?
                  WHERE name = ?'''
    try:
        conn = sqlite3.connect(directory)
    except sqlite3.Error as e:
        print(e)

    for filename in os.listdir('networks/'):
        if filename.endswith(".json"):
            with open(os.path.join('networks/', filename)) as fp:
                cur = conn.cursor()
                asd=cur.execute(sql, [fp.readline(),filename[:-5]])
                conn.commit()


        else:
            continue
