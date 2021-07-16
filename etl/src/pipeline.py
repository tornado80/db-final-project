from db import DB
from psycopg2.sql import SQL, Identifier, Placeholder
from logger import done, loading


class Pipeline:
    def __init__(self, source_db: DB, destination_db: DB):
        self.__source_db = source_db
        self.__destination_db = destination_db

    @staticmethod
    def __condition_maker(identifier: Identifier):
        return SQL("{} = {}").format(identifier, Placeholder())

    def __perform_insertions_and_updates_on_table(self, table_name):
        # create a server-side cursor in source database for a huge data transfer
        source_cursor = self.__source_db.named_cursor("select_cursor")
        destination_cursor = self.__destination_db.cursor
        primary_key, columns = self.__source_db[table_name]
        primary_key_identifiers = [Identifier(prime_attr) for prime_attr in primary_key]
        other_columns = list(set(columns) - set(primary_key))
        other_columns_identifiers = [Identifier(attr) for attr in other_columns]
        all_columns_identifiers = primary_key_identifiers + other_columns_identifiers
        destination_table_name = Identifier(self.__destination_db.schema, table_name)
        source_cursor.execute(
            SQL("SELECT {columns} FROM {table_name};").format(
                columns=SQL(", ").join(all_columns_identifiers),
                table_name=Identifier(self.__source_db.schema, table_name)
            )
        )
        for record in source_cursor:
            destination_cursor.execute(
                SQL("SELECT {primary_key} FROM {table_name} WHERE {conditions};").format(
                    primary_key=SQL(", ").join(primary_key_identifiers),
                    table_name=destination_table_name,
                    conditions=SQL(" AND ").join(map(self.__condition_maker, primary_key_identifiers))
                ), record[:len(primary_key)]
            )
            if destination_cursor.fetchone() is None:
                destination_cursor.execute(
                    SQL("INSERT INTO {table_name} ({columns}) VALUES ({values});").format(
                        table_name=destination_table_name,
                        columns=SQL(", ").join(all_columns_identifiers),
                        values=SQL(", ").join(Placeholder() * len(columns))
                    ), record
                )
            else:
                destination_cursor.execute(
                    SQL("UPDATE {table_name} SET {values} WHERE {conditions};").format(
                        table_name=destination_table_name,
                        values=SQL(", ").join(map(self.__condition_maker, other_columns_identifiers)),
                        conditions=SQL(" AND ").join(map(self.__condition_maker, primary_key_identifiers))
                    ), record[len(primary_key):] + record[:len(primary_key)]
                )
        source_cursor.close()
        destination_cursor.close()

    def __perform_insertions_and_updates(self, topological_order: list):
        print("Performing insertions and updates")
        topological_order.reverse()
        for table_name in topological_order:
            loading(f"Performing insertions and updates on table {table_name}")
            self.__perform_insertions_and_updates_on_table(table_name)
            done()

    def __perform_deletion_on_table(self, table_name):
        source_cursor = self.__source_db.cursor
        # create a server-side cursor in destination database for a huge data transfer
        destination_select_cursor = self.__destination_db.named_cursor("select_cursor")
        destination_delete_cursor = self.__destination_db.cursor
        primary_key, columns = self.__destination_db[table_name]
        primary_key_identifiers = [Identifier(prime_attr) for prime_attr in primary_key]
        other_columns = list(set(columns) - set(primary_key))
        other_columns_identifiers = [Identifier(attr) for attr in other_columns]
        all_columns_identifiers = primary_key_identifiers + other_columns_identifiers
        destination_table_name = Identifier(self.__destination_db.schema, table_name)
        destination_select_cursor.execute(
            SQL("SELECT {columns} FROM {table_name};").format(
                columns=SQL(", ").join(all_columns_identifiers),
                table_name=destination_table_name
            )
        )
        for record in destination_select_cursor:
            source_cursor.execute(
                SQL("SELECT {primary_key} FROM {table_name} WHERE {conditions};").format(
                    primary_key=SQL(", ").join(primary_key_identifiers),
                    table_name=Identifier(self.__source_db.schema, table_name),
                    conditions=SQL(" AND ").join(map(self.__condition_maker, primary_key_identifiers))
                ), record[:len(primary_key)]
            )
            if source_cursor.fetchone() is None:
                destination_delete_cursor.execute(
                    SQL("DELETE FROM {table_name} WHERE {conditions};").format(
                        table_name=destination_table_name,
                        conditions=SQL(" AND ").join(map(self.__condition_maker, primary_key_identifiers))
                    ), record[:len(primary_key)]
                )
        source_cursor.close()
        destination_select_cursor.close()
        destination_delete_cursor.close()

    def __perform_deletions(self, topological_order: list):
        print("Performing deletions")
        for table_name in topological_order:
            loading(f"Performing deletions on table {table_name}")
            self.__perform_deletion_on_table(table_name)
            done()

    def run(self):
        self.__source_db.connect()
        self.__destination_db.connect()
        self.__check_conditions()
        self.__source_db.fetch_tables_columns()
        topological_order = self.__source_db.dag.topological_order
        self.__perform_insertions_and_updates(topological_order.copy())
        self.__perform_deletions(topological_order.copy())
        self.__source_db.close()
        self.__destination_db.close()
        print("Done")

    def __check_conditions(self):
        pass
