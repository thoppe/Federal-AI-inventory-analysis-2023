'''
Collates all the responses from cleaned_responses/ into a single file.
Runs basic analysis checks to verify that there are no unusual columns.
'''
import pandas as pd
from pathlib import Path

expected_cols = [
    'Title',
    'Summary',
]
optional_cols = [
    'Agency',
    'Department',
    'Development Stage',
    'Techniques',
    'Source Code',
]

data = []

for f0 in Path("cleaned_responses/").glob("*.csv"):
    df = pd.read_csv(f0)
    cols = df.columns

    for col in expected_cols:
        if col not in df.columns:
            print(f"Missing {col} in {f0}")
    for col in df.columns:
        if col not in optional_cols and col not in expected_cols:
            print(f"Unexpected {col} in {f0}")

    data.append(df)

df = pd.concat(data).reset_index()
print(df)
