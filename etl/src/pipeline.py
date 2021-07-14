from db import DB


class Pipeline:
    def __init__(self, source_db: DB, destination_db: DB):
        self.__source_db = source_db
        self.__destination_db = destination_db

    def run(self):
        self.__source_db.connect()
        print(self.__source_db.dag().topological_order())
        self.__source_db.close()