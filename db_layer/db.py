import sqlite3

from utils import Singleton


class DbConnection(metaclass=Singleton):
    conn: sqlite3.Connection = None

    def __init__(self):
        # todo: make dependency on dir execution
        self.conn = sqlite3.connect('example.db')

    def init_table(self):
        query = '''
            create table if not exists DTF_IMAGES 
            (
            data_id int not null unique,
            link text not null, 
            likes int not null, 
            processed bool not null default 0, 
            created_at text default current_timestamp, 
            approved_by_me bool default 0)
        '''
        self.cursor.execute(query)
        self.conn.commit()

    @property
    def cursor(self):
        return self.conn.cursor()

    def insert_dtf_record(self, data_id: int, link: str, likes: int, processed: bool):
        values = (data_id, link, likes, processed)
        query = "insert or ignore into " \
                "DTF_IMAGES(data_id, link, likes, processed) " \
                "values (?, ?, ?, ?)"
        self.cursor.execute(query, values)
        self.conn.commit()

    def insert_many_dtf_records(self, records):
        query = "insert or ignore into " \
                "dtf_images(data_id, link, likes) " \
                "values (?, ?, ?)"
        self.cursor.executemany(query, records)
        self.conn.commit()

    def update_dtf_links(self, values: list):
        query = "update dtf_images set processed=? where link=?"
        self.cursor.executemany(query, values)
        self.conn.commit()

    def select_dtf_links_by_processing(self, processed: bool = False):
        values = (processed, )
        query = 'select link from dtf_images where processed=?'
        rows = self.cursor.execute(query, values).fetchall()
        print(rows)

        return rows

    def __del__(self):
        try:
            self.conn.close()
            print('Connection closed')
        except Exception as exc:
            print('Connection doesnt closed because of ', exc)


db = DbConnection()
db.init_table()

# db.init_table()

# values = [(1, 'link3', 100000, False), (2, 'link4', 4356, True)]
# values = [(False, 'link56'), ]
# db.update_dtf_links(values)

# db.insert_many_dtf_records(values)

# db.insert_dtf_record('some link', 10, False)
# db.select_dtf_rows(True)


