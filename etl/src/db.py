import psycopg2
from dag import DAG
from logger import loading, done

class DB:
    def __init__(self, dbname, user, password, host=None, port=None, schema=None):
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port
        self.__schema = "public" if schema is None else schema
        self.__connection = None
        self.__primary_keys = {}
        self.__columns = {}
        self.__dag = None

    @property
    def cursor(self):
        return self.__connection.cursor()

    def named_cursor(self, name):
        return self.__connection.cursor(name)

    @property
    def schema(self):
        return self.__schema

    @property
    def tables(self) -> set:
        return set(self.__columns.keys())

    def connect(self):
        kwargs = {"dbname": self.__dbname,
                  "user": self.__user,
                  "password": self.__password}
        if self.__host is not None:
            kwargs["host"] = self.__host
        if self.__port is not None:
            kwargs["port"] = self.__port
        self.__connection = psycopg2.connect(**kwargs)
        print(f"Successfully connected to database {self.__dbname} as {self.__user} ({self})")

    def __getitem__(self, table_name):
        return self.__primary_keys[table_name], self.__columns[table_name]

    def __str__(self):
        base = f"schema {self.__schema} of database {self.__dbname}"
        return base if self.__host is None else base + f" hosted on {self.__host}:{self.__port}"

    def commit(self):
        self.__connection.commit()

    def fetch_tables_columns(self):
        loading("Fetching tables' attributes of", self)
        with self.cursor as cursor:
            cursor.execute("""
                SELECT C.relname, array_agg(A.attname) 
                FROM pg_attribute AS A JOIN pg_class AS C ON A.attrelid = C.oid 
                WHERE C.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
                AND C.relkind = 'r' AND A.attstattarget < 0
                GROUP BY C.relname;
            """, (self.__schema,))
            tables = cursor.fetchall()
            self.commit()
        done()

        for table_name, columns in tables:
            self.__columns[table_name] = columns

    def __add_nodes_to_dag(self, dag: DAG, cursor):
        loading("Fetching tables' name and primary key of", self)
        cursor.execute("""
            SELECT CL.relname, array_agg(A.attname) 
            FROM pg_constraint AS CO, pg_class AS CL, pg_attribute as A
            WHERE CO.conrelid = CL.oid AND A.attrelid = CL.oid 
            AND CO.contype = 'p' AND A.attnum = ANY(CO.conkey)
            AND CL.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s)
            GROUP BY CL.relname;
        """, (self.__schema,))
        tables = cursor.fetchall()
        self.commit()
        done()

        for table_name, primary_keys in tables:
            dag.add_node(table_name)
            self.__primary_keys[table_name] = primary_keys

    def __add_edges_to_dag(self, dag: DAG, cursor):
        loading("Fetching tables' foreign keys of", self)
        cursor.execute("""
            SELECT B.relname, C.relname 
            FROM pg_constraint as A, pg_class as B, pg_class as C 
            WHERE A.conrelid = B.oid AND A.confrelid = C.oid 
            AND A.connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s) 
            GROUP BY B.relname, C.relname;
        """, (self.__schema,))
        foreign_keys = cursor.fetchall()
        self.commit()
        done()

        for a, b in foreign_keys:
            dag.add_outgoing_edge(a, b)

    def does_any_unique_constraint_exist(self) -> bool:
        loading("Finding unique constraints of", self)
        with self.cursor as cursor:
            cursor.execute("""
                SELECT conrelid FROM pg_constraint WHERE contype = 'u'
                AND connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s) 
                GROUP BY conrelid;
            """, (self.__schema,))
            relations = cursor.fetchone()
            self.commit()
        done()
        if relations is None:
            return False
        return True

    def does_any_self_referencing_exist(self) -> bool:
        loading("Finding self-referencing relations of", self)
        with self.cursor as cursor:
            cursor.execute("""
                SELECT conrelid FROM pg_constraint 
                WHERE contype = 'f' AND conrelid = confrelid 
                AND connamespace = (SELECT oid FROM pg_namespace WHERE nspname = %s) 
                GROUP BY conrelid;
            """, (self.__schema,))
            relations = cursor.fetchone()
            self.commit()
        done()
        if relations is None:
            return False
        return True

    @property
    def dag(self) -> DAG:
        if self.__dag is not None:
            return self.__dag
        print("Creating tables' dependencies DAG of", self)
        dag = DAG(str(self))
        with self.cursor as cursor:
            self.__add_nodes_to_dag(dag, cursor)
            self.__add_edges_to_dag(dag, cursor)
        self.__dag = dag
        print("DAG creation done")
        return dag

    def close(self):
        self.__connection.close()
        print("Disconnected from", self)
