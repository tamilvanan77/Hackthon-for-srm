"""
Dropout Risk Prediction Model
Uses RandomForestClassifier with explainability features.
"""

import pandas as pd
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


class DropoutRiskModel:
    """Explainable neural network dropout risk prediction model."""

    FEATURE_COLS = [
        "attendance", "math_score", "science_score", "language_score",
        "distance_km", "engagement_score",
        "meal_participation_encoded", "sibling_dropout_encoded",
        "family_income_encoded", "parent_education_encoded",
    ]

    FEATURE_LABELS = {
        "attendance": "Attendance %",
        "math_score": "Math Score",
        "science_score": "Science Score",
        "language_score": "Language Score",
        "distance_km": "Distance from School (km)",
        "engagement_score": "School Engagement Score",
        "meal_participation_encoded": "Mid-Day Meal Participation",
        "sibling_dropout_encoded": "Sibling Dropout History",
        "family_income_encoded": "Family Income Level",
        "parent_education_encoded": "Parent Education Level",
    }

    def __init__(self):
        # Using a Multi-Layer Perceptron (Neural Network)
        self.model = MLPClassifier(
            hidden_layer_sizes=(64, 32),
            activation='relu',
            solver='adam',
            max_iter=1000,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.encoders = {}
        self.is_trained = False
        self.accuracy = 0.0
        self.feature_importances = {}

    def _encode_data(self, df):
        """Encode categorical columns."""
        df = df.copy()

        cat_cols = {
            "meal_participation": "meal_participation_encoded",
            "sibling_dropout": "sibling_dropout_encoded",
            "family_income": "family_income_encoded",
            "parent_education": "parent_education_encoded",
        }

        for col, encoded_col in cat_cols.items():
            if col in df.columns:
                if col not in self.encoders:
                    le = LabelEncoder()
                    df[encoded_col] = le.fit_transform(df[col].astype(str))
                    self.encoders[col] = le
                else:
                    le = self.encoders[col]
                    df[encoded_col] = df[col].astype(str).map(
                        lambda x, le=le: (
                            le.transform([x])[0] if x in le.classes_ else 0
                        )
                    )

        return df

    def train(self, df):
        """Train the neural network on student data."""
        df = self._encode_data(df)

        X = df[self.FEATURE_COLS]
        y = df["dropout_risk"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale features for the Neural Network
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test_scaled)
        self.accuracy = accuracy_score(y_test, y_pred)

        # Heuristic for feature importance in MLP:
        # Sum of absolute weights from the first layer for each input
        raw_importances = np.sum(np.abs(self.model.coefs_[0]), axis=1)
        importances = raw_importances / np.sum(raw_importances)
        self.feature_importances = dict(zip(self.FEATURE_COLS, importances))

        return self.accuracy

    def predict_risk(self, student_data):
        """
        Predict dropout risk for a single student using the Neural Network.
        Returns risk_score (0-100).
        """
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first.")

        if isinstance(student_data, dict):
            student_data = pd.DataFrame([student_data])

        student_data = self._encode_data(student_data)

        # Ensure all feature columns exist
        for col in self.FEATURE_COLS:
            if col not in student_data.columns:
                student_data[col] = 0

        X = student_data[self.FEATURE_COLS]
        X_scaled = self.scaler.transform(X)
        
        risk_prob = self.model.predict_proba(X_scaled)[0]

        # Index 1 = probability of dropout
        risk_score = round(risk_prob[1] * 100, 1) if len(risk_prob) > 1 else round(risk_prob[0] * 100, 1)

        return risk_score

    def predict_batch(self, df):
        """Predict risk for all students in a DataFrame using the Neural Network."""
        if not self.is_trained:
            raise ValueError("Model not trained yet.")

        df = self._encode_data(df)

        for col in self.FEATURE_COLS:
            if col not in df.columns:
                df[col] = 0

        X = df[self.FEATURE_COLS]
        X_scaled = self.scaler.transform(X)
        
        probs = self.model.predict_proba(X_scaled)

        risk_scores = []
        for prob in probs:
            score = round(prob[1] * 100, 1) if len(prob) > 1 else round(prob[0] * 100, 1)
            risk_scores.append(score)

        return risk_scores

    def get_top_factors(self, student_data, top_n=3):
        """
        Get top N contributing factors for a specific student's risk.
        Returns list of dicts with factor name, importance, direction, and student value.
        """
        if not self.is_trained:
            return []

        if isinstance(student_data, dict):
            student_data = pd.DataFrame([student_data])

        student_data = self._encode_data(student_data)

        for col in self.FEATURE_COLS:
            if col not in student_data.columns:
                student_data[col] = 0

        # Compute personalized factor contribution
        factors = []
        row = student_data.iloc[0]

        factor_analysis = {
            "attendance": {
                "threshold": 65,
                "direction": "low",
                "desc_bad": "Low attendance",
                "desc_good": "Good attendance",
            },
            "math_score": {
                "threshold": 50,
                "direction": "low",
                "desc_bad": "Low math score",
                "desc_good": "Good math score",
            },
            "science_score": {
                "threshold": 50,
                "direction": "low",
                "desc_bad": "Low science score",
                "desc_good": "Good science score",
            },
            "language_score": {
                "threshold": 55,
                "direction": "low",
                "desc_bad": "Low language score",
                "desc_good": "Good language score",
            },
            "distance_km": {
                "threshold": 5,
                "direction": "high",
                "desc_bad": "Long distance from school",
                "desc_good": "Near to school",
            },
            "engagement_score": {
                "threshold": 55,
                "direction": "low",
                "desc_bad": "Low school engagement",
                "desc_good": "Good school engagement",
            },
            "sibling_dropout_encoded": {
                "threshold": 0.5,
                "direction": "high",
                "desc_bad": "Sibling has dropped out",
                "desc_good": "No sibling dropout",
            },
            "family_income_encoded": {
                "threshold": None,
                "direction": "special",
                "desc_bad": "Low family income",
                "desc_good": "Adequate family income",
            },
            "parent_education_encoded": {
                "threshold": None,
                "direction": "special",
                "desc_bad": "Low parent education",
                "desc_good": "Adequate parent education",
            },
            "meal_participation_encoded": {
                "threshold": 0.5,
                "direction": "low",
                "desc_bad": "Not participating in mid-day meal",
                "desc_good": "Participating in mid-day meal",
            },
        }

        for feat in self.FEATURE_COLS:
            val = row[feat]
            importance = self.feature_importances.get(feat, 0)
            info = factor_analysis.get(feat, {})

            # Calculate risk contribution based on whether student's value is risky
            is_risky = False
            if info.get("direction") == "low" and info.get("threshold"):
                is_risky = val < info["threshold"]
            elif info.get("direction") == "high" and info.get("threshold"):
                is_risky = val > info["threshold"]

            # Weight = model importance × whether this factor is risky for this student
            contrib = importance * (2.0 if is_risky else 0.5)

            factors.append({
                "feature": feat,
                "label": self.FEATURE_LABELS.get(feat, feat),
                "value": val,
                "importance": round(importance * 100, 1),
                "contribution": round(contrib * 100, 1),
                "is_risk_factor": is_risky,
                "description": info.get("desc_bad") if is_risky else info.get("desc_good", ""),
                "direction": "↓ Contributing to risk" if is_risky else "✓ Positive indicator",
            })

        # Sort by contribution (highest first)
        factors.sort(key=lambda x: x["contribution"], reverse=True)

        return factors[:top_n]

    def get_cohort_comparison(self, student_data, all_students_df):
        """Compare student indicators against class average."""
        compare_cols = [
            ("attendance", "Attendance %"),
            ("math_score", "Math Score"),
            ("science_score", "Science Score"),
            ("language_score", "Language Score"),
            ("engagement_score", "Engagement Score"),
            ("distance_km", "Distance (km)"),
        ]

        if isinstance(student_data, dict):
            student_row = student_data
        elif isinstance(student_data, pd.Series):
            student_row = student_data.to_dict()
        else:
            student_row = student_data.iloc[0].to_dict()

        # Filter to same class
        student_class = student_row.get("class", None)
        if student_class:
            class_df = all_students_df[all_students_df["class"] == student_class]
        else:
            class_df = all_students_df

        # Successful students (not dropped out)
        success_df = all_students_df[all_students_df["dropout_risk"] == 0]

        comparison = []
        for col, label in compare_cols:
            comparison.append({
                "indicator": label,
                "student_value": student_row.get(col, 0),
                "class_average": round(class_df[col].mean(), 1),
                "successful_average": round(success_df[col].mean(), 1),
            })

        return comparison

    def identify_high_risk_students(self, df, risk_score_col="risk_score"):
        """
        Enhanced high-risk identification using model risk + rule boosts.
        Returns the input DataFrame with `risk_priority` and `high_risk_flag`.
        """
        work = df.copy()
        if risk_score_col not in work.columns:
            work[risk_score_col] = self.predict_batch(work)

        # Rule-based boosts for critical and cumulative vulnerability patterns.
        chronic_absence = work["attendance"] < 55
        severe_academic = (
            (work["math_score"] < 35)
            | (work["science_score"] < 35)
            | (work["language_score"] < 35)
        )
        compounding_social = (
            (work["family_income"] == "low")
            & (work["sibling_dropout"] == "yes")
        )
        disengaged = work["engagement_score"] < 45
        long_distance = work["distance_km"] > 8

        boost = (
            chronic_absence.astype(int) * 12
            + severe_academic.astype(int) * 10
            + compounding_social.astype(int) * 9
            + disengaged.astype(int) * 7
            + long_distance.astype(int) * 4
        )

        work["risk_priority"] = np.clip(work[risk_score_col] + boost, 0, 100).round(1)
        work["high_risk_flag"] = (
            (work["risk_priority"] >= 70)
            | (chronic_absence & severe_academic)
            | (chronic_absence & compounding_social)
        )
        return work
