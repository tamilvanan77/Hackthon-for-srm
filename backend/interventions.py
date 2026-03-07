"""
Evidence-Based Intervention Recommendation Engine
Maps student risk factors to specific, ranked interventions.
"""

import pandas as pd
from datetime import datetime, timedelta


# -------------------------------------------------------------------
# Evidence-based intervention catalog
# -------------------------------------------------------------------
INTERVENTION_CATALOG = [
    {
        "id": "home_visit",
        "name": "Home Visit by Teacher",
        "description": "Teacher visits the student's home to understand barriers and build rapport with parents.",
        "evidence": "Research shows home visits improve attendance by 15-25% (UNICEF, 2020).",
        "triggers": ["low_attendance", "low_engagement"],
        "success_rate": 0.72,
        "priority": 1,
    },
    {
        "id": "counselling",
        "name": "Individual Counselling Session",
        "description": "One-on-one session with school counsellor to address emotional and academic challenges.",
        "evidence": "School counselling reduces dropout rates by 20% (NCERT Study, 2019).",
        "triggers": ["low_scores", "low_engagement", "sibling_dropout"],
        "success_rate": 0.68,
        "priority": 2,
    },
    {
        "id": "peer_buddy",
        "name": "Peer Buddy Assignment",
        "description": "Pair the student with a high-performing, supportive classmate for daily support.",
        "evidence": "Peer mentoring improves academic outcomes by 10-15% (World Bank, 2021).",
        "triggers": ["low_scores", "low_engagement"],
        "success_rate": 0.65,
        "priority": 3,
    },
    {
        "id": "scholarship",
        "name": "Scholarship Application Support",
        "description": "Help the family apply for available scholarships to reduce financial burden.",
        "evidence": "Financial support reduces dropout rates by 30-40% among low-income families (ASER, 2022).",
        "triggers": ["low_income"],
        "success_rate": 0.80,
        "priority": 1,
    },
    {
        "id": "bicycle",
        "name": "Bicycle Scheme Enrollment",
        "description": "Enroll student in government free bicycle scheme to reduce travel burden.",
        "evidence": "Bicycle provision increased attendance by 20-30% for students living >3km (Bihar study, 2018).",
        "triggers": ["long_distance"],
        "success_rate": 0.75,
        "priority": 1,
    },
    {
        "id": "parent_meeting",
        "name": "Parent-Teacher Meeting",
        "description": "Scheduled meeting with parents to discuss the student's progress and support needed.",
        "evidence": "Parental engagement increases school retention by 18% (UNESCO, 2020).",
        "triggers": ["low_attendance", "low_scores", "low_parent_education"],
        "success_rate": 0.62,
        "priority": 2,
    },
    {
        "id": "extra_coaching",
        "name": "After-School Extra Coaching",
        "description": "Additional academic support after school hours to help the student catch up.",
        "evidence": "Remedial coaching improves learning outcomes by 0.3 SD (J-PAL, 2019).",
        "triggers": ["low_scores"],
        "success_rate": 0.70,
        "priority": 2,
    },
    {
        "id": "meal_enrollment",
        "name": "Mid-Day Meal Re-enrollment",
        "description": "Ensure the student is registered for and attending mid-day meals.",
        "evidence": "Mid-day meals increase attendance by 10-12% (PM Poshan data, 2023).",
        "triggers": ["no_meal", "low_income"],
        "success_rate": 0.60,
        "priority": 3,
    },
    {
        "id": "community_mentor",
        "name": "Community Mentor Assignment",
        "description": "Connect the student with a local community leader or volunteer mentor.",
        "evidence": "Community mentoring reduces dropout by 15% in rural areas (Pratham, 2021).",
        "triggers": ["sibling_dropout", "low_parent_education", "low_engagement"],
        "success_rate": 0.58,
        "priority": 3,
    },
    {
        "id": "uniform_support",
        "name": "Free Uniform Provision",
        "description": "Provide free uniforms to reduce economic barrier to school attendance.",
        "evidence": "Free uniforms increase enrollment and attendance by 6-8% (Kenya RCT, 2017).",
        "triggers": ["low_income"],
        "success_rate": 0.55,
        "priority": 3,
    },
]


def _identify_triggers(student):
    """Identify which risk triggers apply to a student."""
    triggers = set()

    attendance = student.get("attendance", 100)
    math_score = student.get("math_score", 100)
    science_score = student.get("science_score", 100)
    language_score = student.get("language_score", 100)
    distance = student.get("distance_km", 0)
    engagement = student.get("engagement_score", 100)
    income = student.get("family_income", "medium")
    sibling = student.get("sibling_dropout", "no")
    meal = student.get("meal_participation", "yes")
    parent_edu = student.get("parent_education", "secondary")

    if attendance < 65:
        triggers.add("low_attendance")
    if math_score < 50 or science_score < 50 or language_score < 50:
        triggers.add("low_scores")
    if distance > 4:
        triggers.add("long_distance")
    if engagement < 55:
        triggers.add("low_engagement")
    if income == "low":
        triggers.add("low_income")
    if sibling == "yes":
        triggers.add("sibling_dropout")
    if meal == "no":
        triggers.add("no_meal")
    if parent_edu in ("none", "primary"):
        triggers.add("low_parent_education")

    return triggers


def recommend_interventions(student, top_n=5):
    """
    Recommend ranked interventions for a student based on their risk profile.
    Returns list of intervention dicts sorted by relevance and success rate.
    """
    triggers = _identify_triggers(student)

    if not triggers:
        return []

    scored = []
    for intervention in INTERVENTION_CATALOG:
        matching_triggers = set(intervention["triggers"]) & triggers
        if matching_triggers:
            # Score = number of matching triggers × success rate
            relevance = len(matching_triggers) / len(intervention["triggers"])
            score = relevance * intervention["success_rate"] * 100
            scored.append({
                **intervention,
                "matching_triggers": list(matching_triggers),
                "relevance_score": round(score, 1),
            })

    scored.sort(key=lambda x: (-x["relevance_score"], x["priority"]))

    return scored[:top_n]


def calculate_outcome(intervention_row):
    """
    Calculate the outcome metrics of an intervention.
    Returns improvement stats.
    """
    att_before = intervention_row.get("attendance_before", 0)
    att_after = intervention_row.get("attendance_after", 0)
    math_before = intervention_row.get("math_before", 0)
    math_after = intervention_row.get("math_after", 0)

    att_change = att_after - att_before
    math_change = math_after - math_before

    return {
        "attendance_change": att_change,
        "attendance_change_pct": round(
            (att_change / att_before * 100) if att_before > 0 else 0, 1
        ),
        "math_change": math_change,
        "math_change_pct": round(
            (math_change / math_before * 100) if math_before > 0 else 0, 1
        ),
        "improved": att_change > 0 or math_change > 0,
    }


def get_intervention_effectiveness(interventions_df):
    """
    Aggregate intervention effectiveness across all records.
    Returns summary grouped by intervention type.
    """
    if interventions_df is None or interventions_df.empty:
        return pd.DataFrame()

    results = []
    for itype in interventions_df["intervention_type"].unique():
        subset = interventions_df[interventions_df["intervention_type"] == itype]

        avg_att_change = (
            subset["attendance_after"] - subset["attendance_before"]
        ).mean()
        avg_math_change = (
            subset["math_after"] - subset["math_before"]
        ).mean()

        improved_count = sum(
            (subset["attendance_after"] > subset["attendance_before"])
            | (subset["math_after"] > subset["math_before"])
        )

        results.append({
            "Intervention": itype,
            "Count": len(subset),
            "Avg Attendance Change": round(avg_att_change, 1),
            "Avg Math Score Change": round(avg_math_change, 1),
            "Success Rate": f"{round(improved_count / len(subset) * 100, 1)}%",
        })

    return pd.DataFrame(results).sort_values("Avg Attendance Change", ascending=False)
