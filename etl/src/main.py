from argparse import ArgumentParser
from pipeline import Pipeline
from db import DB

PROGRAM = "ETL Pipeline"
DESCRIPTION = """ 
Given a source and destination PostgreSQL database, 
it applies an ETL process from source to destination.
"""
DETAILS = ("<dbname>", "<user>", "<password>")
HOST = "<host>"
PORT = "<port>"
SCHEMA = "<schema>"


class Args:
    def __init__(self):
        self.source_db = None
        self.destination_db = None
        self.source_host = None
        self.destination_host = None
        self.source_port = None
        self.destination_port = None
        self.source_schema = None
        self.destination_schema = None


def main():
    parser = ArgumentParser(prog=PROGRAM, description=DESCRIPTION)
    parser.add_argument("-s", "--source-db", required=True, nargs=3, metavar=DETAILS,
                        help="source database information")
    parser.add_argument("-d", "--destination-db", required=True, nargs=3, metavar=DETAILS,
                        help="destination database information")
    parser.add_argument("-sh", "--source-host", metavar=HOST,
                        help="source database host (defaults to localhost)")
    parser.add_argument("-sp", "--source-port", metavar=PORT, type=int,
                        help="source database port (defaults to 5432)")
    parser.add_argument("-ss", "--source-schema", metavar=SCHEMA,
                        help="source database schema (defaults to public)")
    parser.add_argument("-dh", "--destination-host", metavar=HOST,
                        help="destination database host (defaults to localhost)")
    parser.add_argument("-dp", "--destination-port", metavar=PORT, type=int,
                        help="destination database port (defaults to 5432)")
    parser.add_argument("-ds", "--destination-schema", metavar=SCHEMA,
                        help="destination database schema (defaults to public)")

    args = parser.parse_args(
        # "-s db_final_project amirhosein 123456 -d db_course amirhosein 123456".split(),
        namespace=Args())
    source_dbname, source_user, source_password = args.source_db
    destination_dbname, destination_user, destination_password = args.destination_db

    source_db = DB(source_dbname,
                   source_user,
                   source_password,
                   args.source_host,
                   args.source_port,
                   args.source_schema)
    destination_db = DB(destination_dbname,
                        destination_user,
                        destination_password,
                        args.destination_host,
                        args.destination_port,
                        args.destination_schema)

    Pipeline(source_db, destination_db).run()


main()
