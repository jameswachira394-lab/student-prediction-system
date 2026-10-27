from pathlib import Path

import pandas as pd

# 1. Define the file paths
input_path = Path("data/raw/student_performance_dataset.csv")
output_path = Path("data/processed/cleaned_dataset.csv")

# 2. Load the original dataset
df = pd.read_csv(input_path)

# 3. Count duplicates before cleaning
duplicates_before = df.duplicated().sum()

print("Rows before cleaning:", len(df))
print("Duplicate rows found:", duplicates_before)

# 4. Remove exact duplicate rows
df_cleaned = df.drop_duplicates()

# 5. Count duplicates after cleaning
duplicates_after = df_cleaned.duplicated().sum()

print("Rows after cleaning:", len(df_cleaned))
print("Duplicates remaining:", duplicates_after)

# 6. Create the output folder if it does not exist
output_path.parent.mkdir(parents=True, exist_ok=True)

# 7. Save the cleaned dataset
df_cleaned.to_csv(output_path, index=False)

print("Cleaned dataset saved to:", output_path)
