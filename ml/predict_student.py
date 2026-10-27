import joblib
import pandas as pd

# 1. Load the trained model
model = joblib.load("models/pass_status_model.pkl")

# 2. Enter information for one student
student = pd.DataFrame(
    [
        {
            "Gender": "Female",
            "Study_Hours_per_Week": 15,
            "Attendance_Rate": 85.0,
            "Past_Exam_Scores": 70,
            "Parental_Education_Level": "Bachelors",
            "Internet_Access_at_Home": "Yes",
            "Extracurricular_Activities": "Yes",
        }
    ]
)

# 3. Predict the student's pass status
prediction = model.predict(student)[0]

# 4. Display the result
print("Predicted student status:", prediction)

# 5. Display prediction probabilities, if supported
probabilities = model.predict_proba(student)[0]

for label, probability in zip(model.classes_, probabilities):
    print(f"Probability of {label}: {probability:.2%}")
