"""
Dataset Generator for AI Early Warning System
Generates realistic student records with dropout risk labels.
Covers multiple zones and districts across Tamil Nadu.
"""

import pandas as pd
import numpy as np
import random
import os

random.seed(42)
np.random.seed(42)

# -------------------------------------------------------------------
# Student names (mix of South-Indian and North-Indian names)
# -------------------------------------------------------------------
MALE_NAMES = [
    "Ravi", "Arun", "Kumar", "Suresh", "Ajay", "Vijay", "Rahul", "Deepak",
    "Karthik", "Manoj", "Arjun", "Siddharth", "Ganesh", "Harish", "Naveen",
    "Prasad", "Rajesh", "Sathish", "Venkat", "Ashwin", "Dinesh", "Gopal",
    "Hari", "Jagan", "Mohan", "Ramesh", "Surya", "Vikram", "Anand", "Bala",
    "Selvam", "Murugan", "Senthil", "Vignesh", "Pradeep", "Saravanan",
    "Thirumurugan", "Dhanush", "Karthi", "Shankar", "Mani", "Balaji",
    "Santhosh", "Prabhu", "Tamil", "Kumaran", "Velan", "Gokul", "Nishanth",
    "Bharath", "Kishore", "Aravind", "Vasanth", "Logesh", "Nandha",
]

FEMALE_NAMES = [
    "Meena", "Priya", "Divya", "Lakshmi", "Anitha", "Pooja", "Sneha",
    "Nisha", "Kavya", "Swathi", "Deepika", "Gayathri", "Janani", "Keerthi",
    "Lavanya", "Nandhini", "Pavithra", "Revathi", "Sangeetha", "Thulasi",
    "Uma", "Vanitha", "Yamuna", "Bhavani", "Chitra", "Durga", "Eswari",
    "Gowri", "Indira", "Kamala", "Saranya", "Dhivya", "Ranjani", "Swetha",
    "Maha", "Kowsalya", "Hema", "Mythili", "Abinaya", "Shalini",
    "Archana", "Ramya", "Sowmya", "Bhuvana", "Kalpana", "Vaishali",
    "Jeyanthi", "Tamilselvi", "Vasuki", "Devi",
]

# -------------------------------------------------------------------
# Zone / District / School hierarchy
# -------------------------------------------------------------------
ZONE_DISTRICT_MAP = {
    "North Zone": ["Chennai", "Tiruvallur", "Kancheepuram", "Chengalpattu"],
    "South Zone": ["Madurai", "Tirunelveli", "Thoothukudi", "Virudhunagar"],
    "Central Zone": ["Trichy", "Thanjavur", "Pudukkottai", "Nagapattinam"],
    "West Zone": ["Coimbatore", "Salem", "Erode", "Tirupur", "Namakkal"],
    "East Zone": ["Cuddalore", "Villupuram", "Perambalur", "Ariyalur"],
}

DISTRICT_SCHOOLS = {
    # North Zone
    "Chennai": [
        "GHSS Thiruvanmiyur", "GHSS Adyar", "GHSS Velachery",
        "GHSS Madhavaram", "GHSS Ambattur", "GHSS Guindy",
    ],
    "Tiruvallur": ["GHSS Avadi", "GHSS Ponneri", "GHSS Tiruvallur Town"],
    "Kancheepuram": ["GHSS Kancheepuram", "GHSS Sriperumbudur"],
    "Chengalpattu": ["GHSS Tambaram", "GHSS Chromepet", "GHSS Chengalpattu Town"],
    # South Zone
    "Madurai": ["GHSS Madurai East", "GHSS Madurai West", "GHSS Thirumangalam"],
    "Tirunelveli": ["GHSS Tirunelveli Town", "GHSS Palayamkottai"],
    "Thoothukudi": ["GHSS Thoothukudi", "GHSS Kovilpatti"],
    "Virudhunagar": ["GHSS Virudhunagar", "GHSS Sivakasi"],
    # Central Zone
    "Trichy": ["GHSS Trichy Fort", "GHSS Srirangam", "GHSS Thillai Nagar"],
    "Thanjavur": ["GHSS Thanjavur", "GHSS Kumbakonam"],
    "Pudukkottai": ["GHSS Pudukkottai"],
    "Nagapattinam": ["GHSS Nagapattinam", "GHSS Sirkazhi"],
    # West Zone
    "Coimbatore": ["GHSS RS Puram", "GHSS Gandhipuram", "GHSS Singanallur"],
    "Salem": ["GHSS Salem Town", "GHSS Attur"],
    "Erode": ["GHSS Erode", "GHSS Gobichettipalayam"],
    "Tirupur": ["GHSS Tirupur"],
    "Namakkal": ["GHSS Namakkal", "GHSS Rasipuram"],
    # East Zone
    "Cuddalore": ["GHSS Cuddalore", "GHSS Chidambaram"],
    "Villupuram": ["GHSS Villupuram", "GHSS Tindivanam"],
    "Perambalur": ["GHSS Perambalur"],
    "Ariyalur": ["GHSS Ariyalur"],
}

# Flatten lookups
SCHOOL_TO_DISTRICT = {}
SCHOOL_TO_ZONE = {}
for zone, districts in ZONE_DISTRICT_MAP.items():
    for dist in districts:
        for school in DISTRICT_SCHOOLS.get(dist, []):
            SCHOOL_TO_DISTRICT[school] = dist
            SCHOOL_TO_ZONE[school] = zone

ALL_SCHOOLS = list(SCHOOL_TO_DISTRICT.keys())

DROP_OUT_REASONS = [
    "Economic hardship",
    "Long travel distance",
    "Household responsibilities",
    "Low academic confidence",
    "Health issues",
    "Seasonal migration",
    "Early work pressure",
    "Family relocation",
    "Lack of interest",
    "Peer influence",
]

SECTIONS = ["A", "B", "C"]
CLASSES = [6, 7, 8, 9, 10]


def _generate_phone():
    return f"+91-{random.randint(60000, 99999)}-{random.randint(10000, 99999)}"


def _generate_address(school_name):
    locality = school_name.replace("GHSS ", "")
    street_no = random.randint(1, 240)
    streets = ["Main Road", "Cross Street", "Nagar", "Colony", "Avenue"]
    return f"{street_no}, {locality} {random.choice(streets)}"


def generate_students(n=2000):
    """Generate n student records with realistic correlations."""
    data = []

    for i in range(1, n + 1):
        gender = random.choice(["Male", "Female"])
        name = random.choice(MALE_NAMES if gender == "Male" else FEMALE_NAMES)
        student_class = random.choice(CLASSES)
        section = random.choice(SECTIONS)
        school = random.choice(ALL_SCHOOLS)
        district = SCHOOL_TO_DISTRICT[school]
        zone = SCHOOL_TO_ZONE[school]
        state = "Tamil Nadu"

        # Base characteristics
        family_income = random.choices(
            ["low", "medium", "high"], weights=[0.45, 0.40, 0.15]
        )[0]
        parent_education = random.choices(
            ["none", "primary", "secondary", "graduate"],
            weights=[0.25, 0.35, 0.25, 0.15],
        )[0]
        distance_km = round(random.uniform(0.5, 12.0), 1)
        sibling_dropout = random.choices(
            ["yes", "no"], weights=[0.25, 0.75]
        )[0]

        # ---- Correlated features ----
        risk_bias = 0
        if family_income == "low":
            risk_bias += 12
        if parent_education == "none":
            risk_bias += 10
        if distance_km > 5:
            risk_bias += 8
        if sibling_dropout == "yes":
            risk_bias += 10

        attendance = int(np.clip(
            np.random.normal(78 - risk_bias * 0.5, 15), 20, 100
        ))
        math_score = int(np.clip(
            np.random.normal(65 - risk_bias * 0.4, 18), 10, 100
        ))
        science_score = int(np.clip(
            np.random.normal(62 - risk_bias * 0.35, 17), 10, 100
        ))
        language_score = int(np.clip(
            np.random.normal(68 - risk_bias * 0.3, 16), 10, 100
        ))

        meal_participation = random.choices(
            ["yes", "no"],
            weights=[0.8 - (0.1 if attendance < 60 else 0),
                     0.2 + (0.1 if attendance < 60 else 0)],
        )[0]

        engagement_score = int(np.clip(
            np.random.normal(70 - risk_bias * 0.3, 14), 10, 100
        ))

        # ---- Dropout risk label (heuristic) ----
        risk_points = 0
        if attendance < 60:
            risk_points += 2
        elif attendance < 75:
            risk_points += 1
        if math_score < 40:
            risk_points += 2
        elif math_score < 55:
            risk_points += 1
        if distance_km > 6:
            risk_points += 1.5
        elif distance_km > 4:
            risk_points += 0.5
        if sibling_dropout == "yes":
            risk_points += 1.5
        if family_income == "low":
            risk_points += 1.5
        elif family_income == "medium":
            risk_points += 0.3
        if parent_education == "none":
            risk_points += 1
        if engagement_score < 50:
            risk_points += 1
        if meal_participation == "no":
            risk_points += 0.5
        if student_class >= 9:
            risk_points += 0.5

        dropout_risk = 1 if risk_points >= 5 else 0
        dropout_reason = random.choice(DROP_OUT_REASONS) if dropout_risk else "None reported"

        data.append({
            "student_id": i,
            "name": name,
            "gender": gender,
            "class": student_class,
            "section": section,
            "school": school,
            "zone": zone,
            "district": district,
            "state": state,
            "phone": _generate_phone(),
            "address": _generate_address(school),
            "attendance": attendance,
            "math_score": math_score,
            "science_score": science_score,
            "language_score": language_score,
            "meal_participation": meal_participation,
            "distance_km": distance_km,
            "sibling_dropout": sibling_dropout,
            "family_income": family_income,
            "parent_education": parent_education,
            "engagement_score": engagement_score,
            "dropout_reason": dropout_reason,
            "dropout_risk": dropout_risk,
        })

    return pd.DataFrame(data)


def generate_interventions(students_df, n=320):
    """Generate sample intervention records for high-risk students."""
    high_risk = students_df[students_df["dropout_risk"] == 1]
    if len(high_risk) == 0:
        high_risk = students_df.head(20)

    sample_ids = np.random.choice(
        high_risk["student_id"].values,
        size=min(n, len(high_risk)),
        replace=True,
    )

    intervention_types = [
        "Home Visit", "Counselling Session", "Peer Buddy Assignment",
        "Scholarship Application", "Parent-Teacher Meeting",
        "Extra Coaching", "Bicycle Provided", "Uniform Provided",
    ]

    records = []
    for idx, sid in enumerate(sample_ids, 1):
        student = students_df[students_df["student_id"] == sid].iloc[0]
        itype = random.choice(intervention_types)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        date_str = f"2025-{month:02d}-{day:02d}"

        att_before = student["attendance"]
        math_before = student["math_score"]
        improvement = random.uniform(0, 20)
        att_after = min(100, int(att_before + improvement))
        math_after = min(100, int(math_before + improvement * 0.8))

        records.append({
            "intervention_id": idx,
            "student_id": int(sid),
            "intervention_type": itype,
            "date": date_str,
            "notes": f"{itype} conducted for student {sid}",
            "attendance_before": att_before,
            "math_before": math_before,
            "attendance_after": att_after,
            "math_after": math_after,
        })

    return pd.DataFrame(records)


def generate_schemes():
    """Generate government schemes dataset."""
    schemes = [
        {
            "scheme_name": "PM YASASVI Scholarship",
            "type": "Central",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹75,000 per annum scholarship for meritorious students",
            "documents_required": "Aadhaar Card, Income Certificate, School ID, Mark Sheet, Bank Account",
            "active": "yes",
        },
        {
            "scheme_name": "National Means-cum-Merit Scholarship (NMMSS)",
            "type": "Central",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹12,000 per annum for Class 9–12 students",
            "documents_required": "Aadhaar Card, Income Certificate, School ID, Mark Sheet",
            "active": "yes",
        },
        {
            "scheme_name": "PM SHRI School Enhancement",
            "type": "Central",
            "eligibility_income": "any",
            "eligibility_distance": 0,
            "benefit": "Upgraded school infrastructure and learning resources",
            "documents_required": "School Registration, UDISE Code",
            "active": "yes",
        },
        {
            "scheme_name": "Mid-Day Meal Scheme (PM Poshan)",
            "type": "Central",
            "eligibility_income": "any",
            "eligibility_distance": 0,
            "benefit": "Free nutritious lunch for all government school students",
            "documents_required": "School Enrolment Proof",
            "active": "yes",
        },
        {
            "scheme_name": "Tamil Nadu Free Bicycle Scheme",
            "type": "State",
            "eligibility_income": "any",
            "eligibility_distance": 3,
            "benefit": "Free bicycle for students in Class 9 and above",
            "documents_required": "Aadhaar Card, School ID, Address Proof, Distance Certificate",
            "active": "yes",
        },
        {
            "scheme_name": "Tamil Nadu Free Uniform Scheme",
            "type": "State",
            "eligibility_income": "any",
            "eligibility_distance": 0,
            "benefit": "Free school uniforms (4 sets per year)",
            "documents_required": "School Enrolment Proof, Aadhaar Card",
            "active": "yes",
        },
        {
            "scheme_name": "Tamil Nadu Free Textbook Scheme",
            "type": "State",
            "eligibility_income": "any",
            "eligibility_distance": 0,
            "benefit": "Free textbooks and notebooks for all government school students",
            "documents_required": "School Enrolment Proof",
            "active": "yes",
        },
        {
            "scheme_name": "Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme",
            "type": "State",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹1,000 per month for girl students pursuing higher education",
            "documents_required": "Aadhaar Card, Income Certificate, School ID, Bank Account",
            "active": "yes",
        },
        {
            "scheme_name": "Tamil Nadu Chief Minister's Girl Child Protection Scheme",
            "type": "State",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹50,000 deposit maturity on completing Class 12",
            "documents_required": "Aadhaar Card, Birth Certificate, Income Certificate, Bank Account",
            "active": "yes",
        },
        {
            "scheme_name": "Adi Dravidar & Tribal Welfare Scholarship",
            "type": "State",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "Full fee waiver + monthly stipend for SC/ST students",
            "documents_required": "Aadhaar Card, Caste Certificate, Income Certificate, School ID",
            "active": "yes",
        },
        {
            "scheme_name": "Pre-Matric Scholarship for SC Students",
            "type": "Central",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹3,500 per annum for Class 9-10 SC students",
            "documents_required": "Aadhaar Card, Caste Certificate, Income Certificate, Bank Account",
            "active": "yes",
        },
        {
            "scheme_name": "National Scheme of Incentive to Girls for Secondary Education",
            "type": "Central",
            "eligibility_income": "low",
            "eligibility_distance": 0,
            "benefit": "₹3,000 fixed deposit maturing at age 18 for SC/ST girl students",
            "documents_required": "Aadhaar Card, Caste Certificate, School Enrolment, Birth Certificate",
            "active": "yes",
        },
    ]
    return pd.DataFrame(schemes)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Generating student dataset (2000 records)...")
    students = generate_students(2000)
    students.to_csv("data/students.csv", index=False)
    print(f"  → data/students.csv  ({len(students)} rows)")

    high_risk_count = students["dropout_risk"].sum()
    print(f"  → High-risk students: {high_risk_count} / {len(students)}")

    # Zone summary
    for zone in sorted(students["zone"].unique()):
        zone_df = students[students["zone"] == zone]
        z_risk = zone_df["dropout_risk"].sum()
        print(f"  → {zone}: {len(zone_df)} students, {z_risk} high-risk")

    print("Generating intervention records...")
    interventions = generate_interventions(students, 320)
    interventions.to_csv("data/interventions.csv", index=False)
    print(f"  → data/interventions.csv  ({len(interventions)} rows)")

    print("Generating government schemes dataset...")
    schemes = generate_schemes()
    schemes.to_csv("data/schemes.csv", index=False)
    print(f"  → data/schemes.csv  ({len(schemes)} rows)")

    try:
        import sqlalchemy
        from dotenv import load_dotenv
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            print("\nWriting directly to PostgreSQL database...")
            engine = sqlalchemy.create_engine(db_url)
            students.to_sql("students", con=engine, if_exists="replace", index=False)
            interventions.to_sql("interventions", con=engine, if_exists="replace", index=False)
            schemes.to_sql("schemes", con=engine, if_exists="replace", index=False)
            print("  → Database tables updated.")
    except Exception as e:
        print(f"\nSkipped database write (is PostgreSQL running?): {e}")

    print("\n✅ All datasets generated successfully!")
