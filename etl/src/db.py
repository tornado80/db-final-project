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
        print(f"Successfully connected to database {self.__dbname} as {self.__user}")

    def dag(self) -> DAG:
        g = DAG()
        schema = "public" if self.__schema is None else self.__schema

        self.__cursor.execute("""
            SELECT tablename FROM pg_tables WHERE schemaname = %s
        """, (schema,))
        table_names = self.__cursor.fetchall()
        print(f"Fetched table names of database {self.__dbname}")

        for table_name in table_names:
            g.add_node(table_name[0])

        self.__cursor.execute("""
            SELECT B.relname, C.relname FROM pg_constraint as A, pg_class as B, pg_class as C 
            WHERE A.conrelid = B.oid AND A.confrelid = C.oid 
            AND A.connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s) 
            GROUP BY B.relname, C.relname;
        """, (schema,))
        foreign_keys = self.__cursor.fetchall()
        print(f"Fetched foreign keys in database {self.__dbname}")

        for foreign_key in foreign_keys:
            a, b = foreign_key
            g.add_outgoing_edge(a, b)

        return g

    def close(self):
        self.__cursor.close()
        self.__connection.close()
        print(f"Disconnected from database {self.__dbname}")
