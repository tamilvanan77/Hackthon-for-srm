import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/safepath_db")

def setup_database():
    print(f"Connecting to database: {DATABASE_URL}")
    try:
        engine = create_engine(DATABASE_URL)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        
        # Paths to CSVs
        students_csv = os.path.join(data_dir, "students.csv")
        interventions_csv = os.path.join(data_dir, "interventions.csv")
        schemes_csv = os.path.join(data_dir, "schemes.csv")
        
        # Load datasets
        print("Reading CSV files...")
        students_df = pd.read_csv(students_csv)
        interventions_df = pd.read_csv(interventions_csv)
        schemes_df = pd.read_csv(schemes_csv)
        
        # Write to PostgreSQL
        print("Writing to PostgreSQL database tables...")
        students_df.to_sql("students", con=engine, if_exists="replace", index=False)
        print(f"Imported {len(students_df)} students.")
        
        interventions_df.to_sql("interventions", con=engine, if_exists="replace", index=False)
        print(f"Imported {len(interventions_df)} interventions.")
        
        schemes_df.to_sql("schemes", con=engine, if_exists="replace", index=False)
        print(f"Imported {len(schemes_df)} schemes.")
        
        print("\n✅ Database setup complete!")
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nPlease ensure your local PostgreSQL server is running and the database exists.")
        print("You can create the database manually via psql:")
        print("CREATE DATABASE safepath_db;")

if __name__ == "__main__":
    setup_database()
