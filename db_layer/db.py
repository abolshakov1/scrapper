import sqlite3
import pathlib
from utils import Singleton


class DbConnection(metaclass=Singleton):
    conn: sqlite3.Connection = None

    def __init__(self):
        self._init_connection()

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
            approved_by_me bool default 0)
        '''
        self.cursor.execute(query)
        self.conn.commit()

    @property
    def cursor(self):
        return self.conn.cursor()

    def insert_dtf_record(self, data_id: int, link: str, likes: int):
        values = (data_id, link, likes)
        query = "insert or ignore into " \
                "DTF_IMAGES(data_id, link, likes) " \
                "values (?, ?, ?)"
        self.cursor.execute(query, values)
        self.conn.commit()

    def insert_many_dtf_records(self, records):
        query = "insert or ignore into " \
                "dtf_images(data_id, link, likes) " \
                "values (?, ?, ?)"
        self.cursor.executemany(query, records)
        self.conn.commit()

    def update_dtf_links(self, values: list):
        query = "update dtf_images set processed_by_me=?, processed_by_bot=? where link=?"
        self.cursor.executemany(query, values)
        self.conn.commit()

    def select_processed_by_me(self, processed: bool = False):
        values = (processed, )
        query = 'select data_id, link from dtf_images where processed_by_me=?'
        rows = self.cursor.execute(query, values).fetchall()
        print(rows)

        return rows

    def select_processed(self, processed_by_me: bool=True, processed_by_bot: bool=False):
        values = (processed_by_me, processed_by_bot)
        query = 'select from dft_images where processed_by_me=? and processed_by_bot=?'
        rows = self.cursor.execute(query, values).fetchall()

        return rows

    def __del__(self):
        try:
            self.conn.close()
            print('Connection closed')
        except Exception as exc:
            print('Connection doesnt closed because of ', exc)

    def _init_connection(self):
        path = str(pathlib.Path(__file__).parent.resolve().parent) + '\\'
        path += 'scrapper.db'
        print('Db connected to ' + path)

        self.conn = sqlite3.connect(path)

db = DbConnection()

# db.init_table()

# db.init_table()

# values = [(1, 'link3', 100000, False), (2, 'link4', 4356, True)]
# values = [(False, 'link56'), ]
# db.update_dtf_links(values)

# db.insert_many_dtf_records(values)

# db.insert_dtf_record('some link', 10, False)
# db.select_dtf_rows(True)


