from pathlib import Path
import duckdb
from dataclasses import dataclass
import os


@dataclass
class SourceDataset:
    table_name: str
    file_path: Path
    is_spatial: bool = False


def _db_connection(DATABASE_PATH: str) -> duckdb.DuckDBPyConnection:
    connection = duckdb.connect(str(DATABASE_PATH))
    # connection.sql(f"LOAD spatial;")
    print(f"✅ Connection established with: {DATABASE_PATH}")
    return connection


def create_database(DATABASE_PATH: str) -> duckdb.DuckDBPyConnection:
    # delete the database if it exists
    # DATABASE_PATH.unlink(missing_ok=True)
    # create the database
    connection = _db_connection(DATABASE_PATH)
    with _db_connection(DATABASE_PATH) as connection:
        connection.sql(f"INSTALL spatial;")
        connection.sql(f"LOAD spatial;")
    print(f"✅ Created a persistent database at: {DATABASE_PATH}")


def load_source_data(source_datasets: SourceDataset, DATABASE_PATH: str) -> None:
    for dateset in source_datasets:
        print(f"Loading source dataset {dateset}")
        if dateset.is_spatial:
            with _db_connection(DATABASE_PATH) as connection:
                connection.sql(
                    f"CREATE TABLE {dateset.table_name} as SELECT * FROM ST_Read('{dateset.file_path}')"
                )
                connection.sql(f"DESCRIBE TABLE {dateset.table_name}").show()
        else:
            with _db_connection(DATABASE_PATH) as connection:
                connection.sql(f"DESCRIBE TABLE '{dateset.file_path}'").show()
                connection.sql(
                    f"CREATE TABLE {dateset.table_name} as SELECT * FROM '{dateset.file_path}'"
                )
        print(f"✅ Loaded source dataset {dateset.table_name}")
    
    with _db_connection(DATABASE_PATH) as connection:
        connection.sql(f"SHOW ALL TABLES").show()
    print(f"✅ Loaded all source data to database {DATABASE_PATH}")
