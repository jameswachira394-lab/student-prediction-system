import pandas as pd

# Load the already-cleaned dataset
df = pd.read_csv("data/processed/cleaned_dataset.csv")

# Display the current column names
print("Current columns:")
print(df.columns.tolist())

# Rename columns (replace these example names with your actual names)
df = df.rename(columns={
    "Pass_Fail": "Pass_status"
})

# Display the updated column names
print("\nUpdated columns:")
print(df.columns.tolist())

# Save the renamed dataset
df.to_csv("data/processed/cleaned_dataset.csv", index=False)

print("\nColumn names updated successfully.")