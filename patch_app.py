import os

file_path = "app.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    students_csv_path = os.path.join(base, "data", "students.csv")
    students = pd.read_csv(students_csv_path)
    students = ensure_student_schema(students, students_csv_path)
    interventions = pd.read_csv(os.path.join(base, "data", "interventions.csv"))
    schemes = pd.read_csv(os.path.join(base, "data", "schemes.csv"))
    return students, interventions, schemes


@st.cache_resource
def train_model(students_csv_path):
    df = pd.read_csv(students_csv_path)
    model = DropoutRiskModel()
    accuracy = model.train(df)
    return model, accuracy


# Try loading
try:
    all_students_df, interventions_df, schemes_df = load_data()
    base = os.path.dirname(os.path.abspath(__file__))
    model, model_accuracy = train_model(os.path.join(base, "data", "students.csv"))
    # Compute risk scores for all students
    all_students_df["risk_score"] = model.predict_batch(all_students_df)
    all_students_df["risk_level"] = all_students_df["risk_score"].apply(
        lambda x: "High" if x > 60 else ("Medium" if x > 35 else "Low")
    )
    all_students_df = model.identify_high_risk_students(all_students_df)
except FileNotFoundError:
    st.error("⚠️ Data files not found. Please run `python generate_data.py` first to generate datasets.")
    st.stop()"""

replacement = """import sqlalchemy
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:2005@localhost:5432/safepath_db")

@st.cache_resource
def get_db_engine():
    return sqlalchemy.create_engine(DATABASE_URL)


@st.cache_data
def load_data():
    try:
        engine = get_db_engine()
        students = pd.read_sql("SELECT * FROM students", con=engine)
        interventions = pd.read_sql("SELECT * FROM interventions", con=engine)
        schemes = pd.read_sql("SELECT * FROM schemes", con=engine)
        return students, interventions, schemes
    except Exception as e:
        st.error(f"Error loading data from database: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


@st.cache_resource
def train_model():
    engine = get_db_engine()
    df = pd.read_sql("SELECT * FROM students", con=engine)
    if "location_type" not in df.columns:
        df["location_type"] = "City"
    model = DropoutRiskModel()
    accuracy = model.train(df)
    return model, accuracy


# Try loading
try:
    all_students_df, interventions_df, schemes_df = load_data()
    model, model_accuracy = train_model()
    if not all_students_df.empty:
        # Compute risk scores for all students
        all_students_df["risk_score"] = model.predict_batch(all_students_df)
        all_students_df["risk_level"] = all_students_df["risk_score"].apply(
            lambda x: "High" if x > 60 else ("Medium" if x > 35 else "Low")
        )
        all_students_df = model.identify_high_risk_students(all_students_df)
except Exception as e:
    st.error(f"⚠️ Error initializing app with database: {e}")
    st.stop()"""

# normalize line endings for replace
content_norm = content.replace('\\r\\n', '\\n')
target_norm = target.replace('\\r\\n', '\\n')

if target_norm in content_norm:
    new_content = content_norm.replace(target_norm, replacement)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully replaced content in app.py")
else:
    print("Target content not found in app.py. Here is a piece of the content around load_data:")
    idx = content_norm.find('def load_data():')
    if idx != -1:
        print(content_norm[max(0, idx-50):idx+500])
