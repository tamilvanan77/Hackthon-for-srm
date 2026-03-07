"""
Context-aware AI assistant for the dropout warning dashboard.
Supports zone/school risk analysis, student queries, and summaries.
"""

import pandas as pd


def _zone_risk_analysis(students_df):
    """Compute risk stats per zone."""
    zones = []
    for zone in sorted(students_df["zone"].dropna().unique()):
        z = students_df[students_df["zone"] == zone]
        total = len(z)
        high = int((z["risk_level"] == "High").sum()) if "risk_level" in z.columns else 0
        avg_att = round(float(z["attendance"].mean()), 1)
        risk_pct = round(high / total * 100, 1) if total else 0
        zones.append({
            "zone": zone, "total": total, "high_risk": high,
            "risk_pct": risk_pct, "avg_attendance": avg_att,
        })
    return sorted(zones, key=lambda x: x["risk_pct"], reverse=True)


def _school_risk_analysis(students_df, top_n=5):
    """Compute risk stats per school, return top N riskiest."""
    schools = []
    for school in students_df["school"].dropna().unique():
        s = students_df[students_df["school"] == school]
        total = len(s)
        high = int((s["risk_level"] == "High").sum()) if "risk_level" in s.columns else 0
        avg_att = round(float(s["attendance"].mean()), 1)
        risk_pct = round(high / total * 100, 1) if total else 0
        zone = s["zone"].iloc[0] if "zone" in s.columns else "Unknown"
        district = s["district"].iloc[0] if "district" in s.columns else "Unknown"
        schools.append({
            "school": school, "zone": zone, "district": district,
            "total": total, "high_risk": high,
            "risk_pct": risk_pct, "avg_attendance": avg_att,
        })
    return sorted(schools, key=lambda x: x["risk_pct"], reverse=True)[:top_n]


def generate_chatbot_response(user_query, students_df, selected_student=None):
    q = (user_query or "").strip().lower()
    if not q:
        return "Please ask a question about risk, attendance, interventions, zones, schools, or a student."

    total = len(students_df)
    high = int((students_df["risk_level"] == "High").sum()) if "risk_level" in students_df.columns else 0
    flagged = int(students_df.get("high_risk_flag", pd.Series(dtype=bool)).sum()) if "high_risk_flag" in students_df.columns else high
    avg_att = round(float(students_df["attendance"].mean()), 1) if total else 0.0

    # --- Zone risk queries ---
    if any(kw in q for kw in ["zone risk", "which zone", "highest risk zone", "riskiest zone", "zone analysis", "compare zone"]):
        zone_stats = _zone_risk_analysis(students_df)
        if not zone_stats:
            return "No zone data available in the current filter."
        lines = ["**Zone Risk Analysis** (sorted by risk %):\n"]
        for i, z in enumerate(zone_stats, 1):
            emoji = "🔴" if z["risk_pct"] > 40 else ("🟡" if z["risk_pct"] > 25 else "🟢")
            lines.append(
                f"{emoji} **{z['zone']}** — {z['high_risk']}/{z['total']} high-risk "
                f"({z['risk_pct']}%), Avg attendance: {z['avg_attendance']}%"
            )
        top = zone_stats[0]
        lines.append(f"\n⚠️ **{top['zone']}** has the highest dropout risk at {top['risk_pct']}%.")
        return "\n".join(lines)

    # --- Specific zone query ---
    if "zone" in q:
        for zone in students_df["zone"].dropna().unique():
            if zone.lower().replace(" zone", "").replace(" ", "") in q.replace(" zone", "").replace(" ", ""):
                z = students_df[students_df["zone"] == zone]
                z_total = len(z)
                z_high = int((z["risk_level"] == "High").sum()) if "risk_level" in z.columns else 0
                z_avg = round(float(z["attendance"].mean()), 1)
                districts = z["district"].nunique()
                schools = z["school"].nunique()
                return (
                    f"**{zone} Analysis:**\n"
                    f"- Students: {z_total}\n"
                    f"- High Risk: {z_high} ({round(z_high/z_total*100,1) if z_total else 0}%)\n"
                    f"- Avg Attendance: {z_avg}%\n"
                    f"- Districts: {districts}\n"
                    f"- Schools: {schools}"
                )

    # --- High risk schools ---
    if any(kw in q for kw in ["high risk school", "riskiest school", "worst school", "top school"]):
        top_schools = _school_risk_analysis(students_df, top_n=5)
        if not top_schools:
            return "No school data available."
        lines = ["**Top 5 High-Risk Schools:**\n"]
        for i, s in enumerate(top_schools, 1):
            lines.append(
                f"{i}. **{s['school']}** ({s['district']}, {s['zone']}) — "
                f"{s['high_risk']}/{s['total']} high-risk ({s['risk_pct']}%), "
                f"Avg attendance: {s['avg_attendance']}%"
            )
        return "\n".join(lines)

    # --- Summary / overview ---
    if any(kw in q for kw in ["summary", "overview", "status", "dashboard"]):
        zone_count = students_df["zone"].nunique() if "zone" in students_df.columns else 0
        district_count = students_df["district"].nunique() if "district" in students_df.columns else 0
        school_count = students_df["school"].nunique() if "school" in students_df.columns else 0
        return (
            f"**System Summary:**\n"
            f"- Total students: {total}\n"
            f"- High-risk (model): {high}\n"
            f"- Enhanced high-risk flags: {flagged}\n"
            f"- Average attendance: {avg_att}%\n"
            f"- Zones: {zone_count} | Districts: {district_count} | Schools: {school_count}"
        )

    # --- Priority students ---
    if any(kw in q for kw in ["high risk", "priority", "top risk"]):
        col = "risk_priority" if "risk_priority" in students_df.columns else "risk_score"
        top = students_df.sort_values(col, ascending=False).head(5)
        if top.empty:
            return "No students available in the current filter."
        lines = ["**Top priority students:**\n"]
        for _, row in top.iterrows():
            school = row.get("school", "")
            zone = row.get("zone", "")
            lines.append(
                f"- {int(row['student_id'])} — {row['name']} | "
                f"Priority {row.get('risk_priority', row.get('risk_score', 0))}, "
                f"Attendance {row['attendance']}% | {school} ({zone})"
            )
        return "\n".join(lines)

    # --- Attendance ---
    if "attendance" in q:
        low_att = int((students_df["attendance"] < 65).sum())
        very_low = int((students_df["attendance"] < 50).sum())
        return (
            f"**Attendance Report:**\n"
            f"- Below 65%: {low_att} students\n"
            f"- Below 50% (critical): {very_low} students\n"
            f"- Average: {avg_att}%"
        )

    # --- Student context ---
    if selected_student is not None and ("this student" in q or "student" in q or "action" in q):
        return (
            f"**{selected_student['name']}** — Class {selected_student['class']}{selected_student['section']}\n"
            f"- Risk Score: {selected_student['risk_score']}  |  Priority: {selected_student.get('risk_priority', 'N/A')}\n"
            f"- Attendance: {selected_student['attendance']}%  |  School: {selected_student.get('school', 'N/A')}\n"
            f"- Zone: {selected_student.get('zone', 'N/A')}  |  District: {selected_student.get('district', 'N/A')}\n\n"
            f"**Suggested actions:** Parent-teacher meeting, attendance follow-up, "
            f"and check eligible government schemes."
        )

    return (
        "I can help with:\n"
        "- `summary` — overall system status\n"
        "- `which zone has highest risk?` — zone risk analysis\n"
        "- `high risk schools` — top 5 riskiest schools\n"
        "- `north zone` — specific zone breakdown\n"
        "- `top high risk students` — priority student list\n"
        "- `attendance` — attendance report\n"
        "- `what should we do for this student` — action plan"
    )
