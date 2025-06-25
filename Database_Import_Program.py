import os
import pandas as pd
import sqlite3
from glob import glob

def import_cleaned_csvs_to_sqlite(csv_dir, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cleaned_files = glob(os.path.join(csv_dir, "mlb_*_cleaned.csv"))

    for filepath in cleaned_files:
        table_name = os.path.splitext(os.path.basename(filepath))[0]
        print(f"Importing {os.path.basename(filepath)} into table {table_name}...")

        df = pd.read_csv(filepath)

        # Optional column cleaning
        df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_").str.replace("-", "_")
        df = df.loc[:, ~df.columns.duplicated()]

        # Drop table if it already exists
        cursor.execute(f"DROP TABLE IF EXISTS '{table_name}';")

        # Create table SQL
        col_defs = []
        for col, dtype in zip(df.columns, df.dtypes):
            if pd.api.types.is_integer_dtype(dtype):
                sql_type = "INTEGER"
            elif pd.api.types.is_float_dtype(dtype):
                sql_type = "REAL"
            else:
                sql_type = "TEXT"
            col_defs.append(f'"{col}" {sql_type}')
        create_stmt = f"CREATE TABLE '{table_name}' ({', '.join(col_defs)});"
        cursor.execute(create_stmt)

        # Insert data
        df.to_sql(table_name, conn, if_exists='append', index=False)

        print(f"Imported {len(df)} rows into {table_name}.")

    conn.commit()
    conn.close()
    print("All CSV files imported into the database.")
