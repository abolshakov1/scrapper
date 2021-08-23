import sqlite3
import pathlib
from utils import Singleton


class DbConnection:
    conn: sqlite3.Connection = None

    def __init__(self):
        self.init_table()

    """
        processed_by_bot - send or not to public 
        processed_by_me - approved or not by me. need to know if bot got answer from me. 
                          do not process posts if I didn't answer yet
        approved_by_me - approved by me
        
    """
    def init_table(self):
        query = '''
            create table if not exists DTF_IMAGES 
            (
            data_id int not null unique,
            link text not null, 
            likes int not null, 
            processed_by_bot bool not null default 0, 
            processed_by_me bool not null default 0,
            created_at text default current_timestamp, 
            approved_by_me bool default 0, 
            sent bool default 0)
        '''
        self.cursor.execute(query)
        self.conn.commit()

    @property
    def cursor(self):
        if not self.conn:
            self.open_connection()

        return self.conn.cursor()

    def open_connection(self):
        path = str(pathlib.Path(__file__).parent.resolve().parent) + '/'
        path += 'scrapper.db'
        print('Db connected to ' + path)

        self.conn = sqlite3.connect(path)

    def close_connection(self):
        self.conn.close()
        print('Connection closed')

    def _connection_handler(func):
        def decorate(self, *args, **kwargs):
            self.open_connection()
            result = func(self, *args, **kwargs)
            self.close_connection()

            return result
        return decorate

    def insert_many_dtf_records(self, records):
        query = "insert or ignore into " \
                "dtf_images(data_id, link, likes) " \
                "values (?, ?, ?)"
        self.cursor.executemany(query, records)
        self.conn.commit()

    def update_processed_by_me(self, values: list):
        query = "update dtf_images set processed_by_me=TRUE, approved_by_me=? where data_id=?"
        self.cursor.executemany(query, values)
        self.conn.commit()

    def update_sent(self, ids: list):
        query = "update dtf_images set sent=TRUE where data_id=?"
        self.cursor.executemany(query, ids)
        self.conn.commit()

    @_connection_handler
    def update_processed_by_bot(self, values):
        query = 'update dtf_images set processed_by_bot=TRUE where data_id=?'
        self.cursor.executemany(query, values)
        self.conn.commit()

    def select_unprocessed_and_unsent(self):
        """
        Returns record that didn't send and processed by me yet.
        :return:
        """
        query = 'select data_id, link from dtf_images where processed_by_me=FALSE and sent=FALSE'
        rows = self.cursor.execute(query).fetchall()

        return rows

    @_connection_handler
    def select_records_for_publish(self):
        query = 'select data_id, link from dtf_images where ' \
                'processed_by_me=TRUE and ' \
                'processed_by_bot=FALSE and ' \
                'approved_by_me=TRUE '
        rows = self.cursor.execute(query).fetchall()

        return rows

    def __del__(self):
        try:
            self.close_connection()
        except Exception as exc:
            print('Connection doesnt closed because of ', exc)


if __name__ == "__main__":
    db = DbConnection()
    db.open_connection()

    # print(db.select_records_for_publish())
