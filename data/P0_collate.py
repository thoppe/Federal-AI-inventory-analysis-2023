"""
Collates all the responses from cleaned_responses/ into a single file.
Runs basic analysis checks to verify that there are no unexpected columns.
Gives each entry a new Use_Case_ID.
Checks that the counts match the expected counts
"""
import pandas as pd
from pathlib import Path

expected_cols = [
    "Title",
    "Summary",
]
optional_cols = [
    "Agency",
    "Office",
    "Development Stage",
    "Techniques",
    "Source Code",
]


data = []
info = pd.read_csv("data_ingestion_statistics_AI_inv.csv")
info = info.set_index("Dept Code")

for f0 in Path("cleaned_responses/").glob("*.csv"):
    df = pd.read_csv(f0)
    cols = df.columns

    # Validation checks
    for col in expected_cols:
        if col not in df.columns:
            raise ValueError(f"Missing {col} in {f0}")
    for col in df.columns:
        if col not in optional_cols and col not in expected_cols:
            raise ValueError(f"Unexpected {col} in {f0}")

    # Add a Department acronym and full name
    department_code, year = f0.stem.split("_")
    department_name = info.loc[department_code]["Department"]

    df["Department Code"] = department_code
    df["Department"] = department_name

    # Add Office and Agency if not present
    for key in ["Agency", "Office"]:
        if key not in df:
            df[key] = None

    # Internally sort by Agency then Office
    df = df.sort_values(["Agency", "Office"])
    data.append(df)

    # Add an Inventory ID
    df["Use_Case_ID"] = [f"{department_code}-{n:04d}-{year}" for n in range(len(df))]

# Concatenate all of the files together
df = pd.concat(data).reset_index(drop=True)

# Clean columns that are split over multilines
for key in ["Title", "Agency", "Office", "Techniques", "Development Stage"]:
    df[key] = df[key].str.split().str.join(" ")

# With all data, now sort by Use-Case-ID
df = df.sort_values("Use_Case_ID").set_index("Use_Case_ID")

# Rename the columns to be machine readable
df.columns = [col.replace(" ", "_") for col in df.columns]

# Reorder the columns
column_order = [
    "Department_Code",
    "Agency",
    "Office",
    "Title",
    "Summary",
    "Development_Stage",
    "Techniques",
    "Source_Code",
    "Department",
]
df = df[column_order]

# Check the expected counts
diff = df.groupby("Department_Code").size() - info["Entries"]
diff = diff[~(info["Entries"] == 0)]
diff = diff[diff != 0]
assert len(diff) == 0

# Save the collated dataset
f_save = f"record_level_information_FedAI_{year}.csv"
df.to_csv(f_save)
