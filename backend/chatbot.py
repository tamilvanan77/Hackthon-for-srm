"""
Simple context-aware assistant for the dropout warning dashboard.
"""

import pandas as pd


def generate_chatbot_response(user_query, students_df, selected_student=None):
    q = (user_query or "").strip().lower()
    if not q:
        return "Please ask a question about risk, attendance, interventions, or a student."

    total = len(students_df)
    high = int((students_df["risk_level"] == "High").sum()) if "risk_level" in students_df.columns else 0
    flagged = int(students_df.get("high_risk_flag", pd.Series(dtype=bool)).sum()) if "high_risk_flag" in students_df.columns else high
    avg_att = round(float(students_df["attendance"].mean()), 1) if total else 0.0

    if "summary" in q or "overview" in q or "status" in q:
        return (
            f"Current filtered view has {total} students, {high} high-risk by model tier, "
            f"and {flagged} enhanced high-risk flags. Average attendance is {avg_att}%."
        )

    if "high risk" in q or "priority" in q:
        top = students_df.sort_values("risk_priority", ascending=False).head(5)
        if top.empty:
            return "No students available in the current filter."
        lines = [
            f"{int(row['student_id'])} - {row['name']} (Priority {row['risk_priority']}, Attendance {row['attendance']}%)"
            for _, row in top.iterrows()
        ]
        return "Top priority students:\n" + "\n".join(lines)

    if "attendance" in q:
        low_att = int((students_df["attendance"] < 65).sum())
        return f"{low_att} students have attendance below 65% in the current filtered set."

    if selected_student is not None and ("this student" in q or "student" in q):
        return (
            f"{selected_student['name']} is in Class {selected_student['class']}{selected_student['section']} "
            f"with risk score {selected_student['risk_score']} and priority {selected_student['risk_priority']}. "
            f"Suggested first action: parent-teacher meeting plus attendance follow-up."
        )

    return (
        "I can help with: `summary`, `top high risk students`, `attendance issues`, or "
        "`what should we do for this student`."
    )
