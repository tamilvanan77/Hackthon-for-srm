"""
Government Scheme Matcher
Matches student profiles to eligible government schemes with application checklists.
"""

import pandas as pd


def match_schemes(student, schemes_df):
    """
    Match a student's profile against available government schemes.

    Args:
        student: dict or Series with student data
        schemes_df: DataFrame of government schemes

    Returns:
        list of dicts with matched schemes and eligibility details
    """
    if isinstance(student, pd.Series):
        student = student.to_dict()

    distance = student.get("distance_km", 0)
    income = student.get("family_income", "medium")
    gender = student.get("gender", "Male")
    student_class = student.get("class", 8)

    matched = []

    for _, scheme in schemes_df.iterrows():
        if scheme.get("active", "yes") != "yes":
            continue

        eligible = True
        reasons = []

        # Check income eligibility
        eligibility_income = scheme.get("eligibility_income", "any")
        if eligibility_income != "any":
            if eligibility_income == "low" and income != "low":
                eligible = False
            else:
                reasons.append(f"Family income: {income}")

        # Check distance eligibility
        eligibility_distance = scheme.get("eligibility_distance", 0)
        if eligibility_distance > 0:
            if distance < eligibility_distance:
                eligible = False
            else:
                reasons.append(f"Distance: {distance} km (≥ {eligibility_distance} km required)")

        if eligible:
            docs = scheme.get("documents_required", "")
            doc_list = [d.strip() for d in docs.split(",") if d.strip()]

            matched.append({
                "scheme_name": scheme["scheme_name"],
                "type": scheme.get("type", "Central"),
                "benefit": scheme.get("benefit", ""),
                "eligibility_reasons": reasons if reasons else ["Generally eligible"],
                "documents_required": doc_list,
                "checklist": _generate_checklist(doc_list),
            })

    return matched


def _generate_checklist(documents):
    """Generate a formatted application checklist."""
    checklist = []
    for i, doc in enumerate(documents, 1):
        checklist.append({
            "step": i,
            "document": doc,
            "status": "Pending",
        })
    return checklist


def get_scheme_summary(schemes_df):
    """Get summary statistics of available schemes."""
    if schemes_df is None or schemes_df.empty:
        return {}

    active = schemes_df[schemes_df["active"] == "yes"]

    return {
        "total_schemes": len(active),
        "central_schemes": len(active[active["type"] == "Central"]),
        "state_schemes": len(active[active["type"] == "State"]),
    }
