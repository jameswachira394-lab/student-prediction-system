## AI/ML Module

### Model
- **Algorithm:** Logistic Regression
- **Saved model:** `models/pass_status_model.pkl`
- **Prediction module:** `predictor.py`
- **Target variable:** `Pass_status`

### Input Features
The model uses the following seven features:
- Gender
- Study_Hours_per_Week
- Attendance_Rate
- Past_Exam_Scores
- Parental_Education_Level
- Internet_Access_at_Home
- Extracurricular_Activities

### Model Evaluation
On the current held-out test set:
- Accuracy: 75%
- Pass precision: approximately 55%
- Pass recall: approximately 72%
- Pass F1-score: approximately 63%

These metrics describe the current evaluation split and may vary with different data.

### Running the Prediction Module

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the prediction test:

```bash
python -m unittest test_predictor.py -v
```

### Limitations
Predictions and probabilities are estimates, not guarantees. The model should not be used as the sole basis for academic decisions.

# student-prediction-system
from pathlib import Path
import pandas as pd

# Path to your original dataset
file_path = Path("data/raw/student_performance_dataset.csv")

# Load the dataset
df = pd.read_csv(file_path)

# Display dataset size
print("\n--- DATASET SIZE ---")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

# Display column names
print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

# Display first five rows
print("\n--- FIRST FIVE ROWS ---")
print(df.head())

# Display data types
print("\n--- DATA TYPES ---")
df.info()

# Display missing values
print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

# Display duplicate rows
print("\n--- DUPLICATE ROWS ---")
print(df.duplicated().sum())