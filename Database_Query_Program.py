import sqlite3

def connect_db(db_path):
    return sqlite3.connect(db_path)

def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("\n Available tables:")
    for t in tables:
        print("  -", t[0])
    print()

def run_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        print("\n Query Results:\n")
        print(" | ".join(columns))
        print("-" * 60)
        for row in results[:10]:  # Limit display to first 10 rows
            print(" | ".join(str(item) for item in row))
        print(f"\n {len(results)} rows returned (showing up to 10).\n")

    except Exception as e:
        print(" Error running query:", e)

def main():
    db_path = "mlb_history.db"
    conn = connect_db(db_path)

    while True:
        print("Options:")
        print("  1. List tables")
        print("  2. Run custom SQL query")
        print("  3. Exit")
        choice = input("Enter choice (1/2/3): ")

        if choice == "1":
            list_tables(conn)

        elif choice == "2":
            query = input("Enter your SQL query:\n> ")
            run_query(conn, query)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")

    conn.close()

if __name__ == "__main__":
    main()
