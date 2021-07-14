import psycopg2
from dag import DAG


class DB:
    def __init__(self, dbname, user, password, host=None, port=None, schema="public"):
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__schema = schema
        self.__connection = None
        self.__cursor = None

    @property
    def cursor(self):
        return self.__cursor

    def connect(self):
        kwargs = {"dbname": self.__dbname,
                  "user": self.__user,
                  "password": self.__password}
        if self.__host is not None:
            kwargs["host"] = self.__host
        if self.__port is not None:
            kwargs["port"] = self.__port
        self.__connection = psycopg2.connect(**kwargs)
        self.__cursor = self.__connection.cursor()
        print(f"Successfully connected to database {self.__dbname} as {self.__user}.")

    def dag(self) -> DAG:
        return None

    def close(self):
        self.__cursor.close()
        self.__connection.close()
        print(f"Disconnected from database {self.__dbname}.")
