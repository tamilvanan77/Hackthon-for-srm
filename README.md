# 🎓 AI Early Warning System for Student Dropout Risk

An intelligent early warning system that predicts which government school students are at risk of dropping out — enabling teachers and administrators to intervene before it's too late.

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **🔐 Role-based Access** | Admin and staff/teacher login with role-based student-detail permissions |
| **📊 Dashboard** | KPI cards, risk distribution charts, and enhanced high-risk prioritization |
| **🎯 Risk Analysis** | Per-student dropout risk score with top 3 contributing factors explained |
| **📋 Intervention Playbook** | Evidence-based intervention recommendations ranked by student profile |
| **💬 Parent Communication** | Auto-draft sensitive messages in English & Tamil (letter + WhatsApp) |
| **🏛️ Government Schemes** | Eligibility checker for central & state schemes with application checklists |
| **🗺️ District Heatmap** | School-level risk visualization for district education officers |
| **📈 Intervention Tracker** | Track 30-day outcomes and build evidence for what works |
| **🤖 AI Chatbot** | Ask for filtered summaries, priority students, and intervention guidance |

## ⚙️ Tech Stack

- **Backend**: Python, Scikit-learn (Neural Network Model)
- **Frontend**: Streamlit (Premium Luxe UI)
- **Database**: PostgreSQL (Supabase/Local)
- **Deployment**: Vercel & Cloud Integration
- **Visualization**: Plotly

## 📦 Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup PostgreSQL Database
# Run create_db.py to initialize schema and seed data
python create_db.py

# 3. Configure Environment Variables
# Create a .env file with your DATABASE_URL

# 4. Run the application
streamlit run app.py
```

Open your browser at `http://localhost:8501`

Demo login credentials:
- `admin / admin@123` (read-only student details)
- `staff / staff@123` (editable student details)
- `teacher / teacher@123` (editable student details)

## 📁 Project Structure

```
Student warning/
├── app.py                  # Main Streamlit application
├── generate_data.py        # Dataset generator (2000 students)
├── requirements.txt        # Python dependencies
├── README.md
├── .streamlit/
│   └── config.toml         # Theme configuration
├── backend/
│   ├── __init__.py
│   ├── risk_model.py       # ML model + explainability
│   ├── interventions.py    # Evidence-based recommendations
│   ├── message_generator.py # Parent communication (EN/TN)
│   └── scheme_matcher.py   # Government scheme matcher
└── data/
    ├── students.csv        # Student dataset (generated, 2000 rows)
    ├── interventions.csv   # Intervention log (generated)
    └── schemes.csv         # Government schemes (generated)
```

## 🤖 How the AI Model Works

1. **Neural Network Multi-layer Perceptron** trained on 10 student features for better accuracy
2. **Explainability**: Feature importance shows which factors contribute most
3. **Risk Score**: 0–100 scale (Low < 35 < Medium < 60 < High)
4. **Top 3 Factors**: Each student gets personalized risk factor explanations via the AI model

## 🛡️ Sensitivity Guardrails

- Parent messages **never** use words like _dropout_, _failing_, or _at risk_
- All communication is encouraging and partnership-focused
- Government schemes use only **currently active** central and state schemes
- Interventions are from a **documented evidence base** with citations
