import pandas as pd
import numpy as np
import sys
import os

# Add the project directory to sys.path
sys.path.append(os.getcwd())

from backend.risk_model import DropoutRiskModel

# Create mock data
data = {
    'attendance': np.random.randint(40, 100, 100),
    'math_score': np.random.randint(20, 100, 100),
    'science_score': np.random.randint(20, 100, 100),
    'language_score': np.random.randint(20, 100, 100),
    'distance_km': np.random.randint(1, 20, 100),
    'engagement_score': np.random.randint(30, 100, 100),
    'meal_participation': np.random.choice(['yes', 'no'], 100),
    'sibling_dropout': np.random.choice(['yes', 'no'], 100),
    'family_income': np.random.choice(['low', 'medium', 'high'], 100),
    'parent_education': np.random.choice(['primary', 'secondary', 'none'], 100),
    'dropout_risk': np.random.choice([0, 1], 100)
}
df = pd.DataFrame(data)

print("Initializing Neural Network Model...")
model = DropoutRiskModel()

print("Training Model...")
accuracy = model.train(df)
print(f"Model trained successfully. Accuracy: {accuracy:.2f}")

print("Testing Single Prediction...")
student = df.iloc[0].to_dict()
score = model.predict_risk(student)
print(f"Prediction for single student: {score}")

print("Testing Batch Prediction...")
scores = model.predict_batch(df.head(5))
print(f"Batch predictions: {scores}")

print("Verifying Feature Importances...")
print(f"Importances: {model.feature_importances}")

print("\n✅ Neural Network Verification Complete!")
