import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load local .env for the cloud URL if defined, otherwise prompt
load_dotenv()

def migrate():
    print("🚀 Cloud Data Migration Tool")
    
    cloud_url = os.getenv("CLOUD_DATABASE_URL")
    if not cloud_url:
        cloud_url = input("Enter your Cloud DATABASE_URL: ").strip()
    
    if not cloud_url:
        print("❌ Error: No Cloud DATABASE_URL provided.")
        return

    try:
        print(f"🔗 Connecting to Cloud Database...")
        engine = create_engine(cloud_url)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        
        datasets = {
            "students": os.path.join(data_dir, "students.csv"),
            "interventions": os.path.join(data_dir, "interventions.csv"),
            "schemes": os.path.join(data_dir, "schemes.csv")
        }
        
        for table, path in datasets.items():
            if os.path.exists(path):
                print(f"📦 Uploading {table}...")
                df = pd.read_csv(path)
                df.to_sql(table, con=engine, if_exists="replace", index=False)
                print(f"✅ {table} migrated ({len(df)} rows).")
            else:
                print(f"⚠️ Warning: {path} not found, skipping.")
                
        print("\n✨ Migration complete! Your cloud app is now powered by your local data.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate()
