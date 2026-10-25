from pathlib import Path

import pandas as pd

# Path to your original dataset
file_path = Path("data/processed/cleaned_dataset.csv")

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
