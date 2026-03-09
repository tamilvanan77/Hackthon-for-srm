import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        # Connect to default postgres database to create a new one
        conn = psycopg2.connect(
            user="postgres",
            password="2005",
            host="localhost",
            port="5432",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if safepath_db exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'safepath_db'")
        exists = cursor.fetchone()
        
        if not exists:
            # CREATE DATABASE creates from template1 by default. Let's see if this works now.
            cursor.execute("CREATE DATABASE safepath_db;")
            print("Database 'safepath_db' created successfully.")
        else:
            print("Database 'safepath_db' already exists.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()
