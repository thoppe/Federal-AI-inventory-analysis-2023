from pathlib import Path
import pandas as pd
import json

f_json = "data/GPT_automated_analysis.json"


def preload(f_json, key, sort_key="Department"):
    with open(f_json) as FIN:
        js = json.load(FIN)

    df = pd.DataFrame(js[key])

    if not sort_key:
        return df

    df[sort_key] = df[sort_key].apply(lambda x: x.replace(" ", "_"))

    # Sort by most counted
    sort_idx = df[sort_key].value_counts()
    df = df.set_index(sort_key)  # [idx]
    df["dcount"] = sort_idx
    df = df.sort_values(["dcount", sort_key], ascending=False)
    del df["dcount"]

    return df


save_dest = Path("results")
save_dest.mkdir(exist_ok=True)

###########################################################################
# Save the specific records
records = pd.read_csv("data/record_level_information_FedAI_2023.csv")
records = records.set_index("Use_Case_ID")
record_keys = ["Department_Code", "Title"]

df = preload(f_json, "theme_records", None)
df.index.name = "Use_Case_ID"
df["total_categories"] = df.sum(axis=1)
for key in record_keys:
    df[key] = records[key]
df.to_csv("results/GSA_record_level_theme_score.csv")

df = preload(f_json, "theme_explain", None)
df.index.name = "Use_Case_ID"
df["total_categories"] = df.sum(axis=1)
for key in record_keys:
    df[key] = records[key]
df.to_csv("results/GSA_record_level_theme_explain.csv")


###########################################################################


f_markdown = save_dest / "AI_highlights_by_Department.md"
df = preload(f_json, "department_content")

doc = []
doc.append("# Prominent AI Highlights across Departments")
doc.append("")

for dept, dx in df.groupby("Department", sort=False):
    doc.append(f"- [{dept} ({len(dx)})](#{dept})")
doc.append("")


for dept, dx in df.groupby("Department", sort=False):
    doc.append(f"## {dept}")
    for line in dx["highlight"]:
        doc.append(f"- {line}")
    doc.append("")

markdown = "\n".join(doc)
print(markdown)

with open(f_markdown, "w") as FOUT:
    FOUT.write(markdown)
print(f"Output written to {f_markdown}")

###########################################################################

f_markdown = save_dest / "AI_projects_full_text_by_Department.md"

df = preload(f_json, "record_content")

doc = []
doc.append("# Complete Text of AI Projects by Department / Agencies")
doc.append("")

for dept, dx in df.groupby("Department", sort=False):
    doc.append(f"- [{dept} ({len(dx)})](#{dept})")
doc.append("")

for dept, dx in df.groupby("Department", sort=False):
    dx = dx.sort_values(["Agency", "Office"])
    doc.append(f"## {dept}")
    doc.append(f"")

    for _, row in dx.iterrows():
        affil = [x for x in [dept, row.Agency, row.Office] if x]
        affil = " | ".join(affil)
        title = " ".join(row.Title.split())
        doc.append(f"**{title}**, _{affil}_")

        text = " ".join(row.Summary.split())
        doc.append(f"> {text}")
        doc.append(f"")

markdown = "\n".join(doc)
print(markdown)

with open(f_markdown, "w") as FOUT:
    FOUT.write(markdown)


###########################################################################

f_markdown = save_dest / "AI_projects_summary_text_by_Department.md"

df = preload(f_json, "record_content")

doc = []
doc.append("# Summarized GPT Text for Project Descriptions")
doc.append("")

for dept, dx in df.groupby("Department", sort=False):
    doc.append(f"- [{dept} ({len(dx)})](#{dept})")
doc.append("")

for dept, dx in df.groupby("Department", sort=False):
    dx = dx.sort_values(["Agency", "Office"])
    doc.append(f"## {dept}")
    doc.append(f"")

    for _, row in dx.iterrows():
        affil = [x for x in [dept, row.Agency, row.Office] if x]
        affil = " | ".join(affil)
        title = " ".join(row.Title.split())
        doc.append(f"**{title}**, _{affil}_")

        text = " ".join(row.LLM_summary_text.split())
        doc.append(f"> {text}")
        doc.append(f"")

markdown = "\n".join(doc)
print(markdown)

with open(f_markdown, "w") as FOUT:
    FOUT.write(markdown)


###########################################################################

f_markdown = save_dest / "AI_themes.md"

df = preload(f_json, "theme_content", None)

doc = []
doc.append("# AI Themes throughout the Federal Government")
doc.append("")


for _, row in df.iterrows():
    doc.append(f"## {row.emoji} {row.theme.title()} ({row.positive_observations})")
    doc.append(f"")
    doc.append(f"{row.description}")
    doc.append(f"")

markdown = "\n".join(doc)
print(markdown)

with open(f_markdown, "w") as FOUT:
    FOUT.write(markdown)
