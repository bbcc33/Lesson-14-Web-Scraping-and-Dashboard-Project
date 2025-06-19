import os
import pandas as pd
import sqlite3

def infer_dtype(series):
    """Infer and return the SQLite-compatible dtype for a pandas Series."""
    if pd.api.types.is_integer_dtype(series):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(series):
        return "REAL"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "DATETIME"
    else:
        return "TEXT"
    
def import_csvs_to_sqlite(csv_dir, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for filename in os.listdir(csv_dir):
        if filename.endswith(".csv"):
            filepath = os.path.join(csv_dir, filename)
            table_name = os.path.splitext(filename)[0]

            print(f"Importing {filename} into table `{table_name}`...")

            try:
                df = pd.read_csv(filepath)

                df.columns = [col.strip().replace(" ", "_").replace("-", "_") for col in df.columns]

                column_types = {col: infer_dtype(df[col]) for col in df.columns}
                column_defs = ", ".join(f'"{col}" {dtype}' for col, dtype in column_types.items())

                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`;")
                cursor.execute(f"CREATE TABLE `{table_name}` ({column_defs});")

                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"{table_name} imported successfully.")
            except Exception as e:
                print(f"Failed to import {filename}: {e}")

    conn.close()
    print("All CSV files imported into the database.")

if __name__ == "__main__":
    import_csvs_to_sqlite(csv_dir="mlb_yearly_data", db_path="mlb_history.db")