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


###########################################################################

f_markdown = "results/AI_highlights_by_Department.md"
df = preload(f_json, "department_content")

doc = []
doc.append("# AI highlights across Departments")
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

f_markdown = "results/AI_projects_full_text_by_Department.md"

df = preload(f_json, "record_content")

doc = []
doc.append("# AI projects across Departments")
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

f_markdown = "results/AI_projects_summary_text_by_Department.md"

df = preload(f_json, "record_content")

doc = []
doc.append("# AI projects across Departments")
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

f_markdown = "results/AI_themes.md"

df = preload(f_json, "theme_content", None)

doc = []
doc.append("# AI project themes across the Federal government")
doc.append("")


for _, row in df.iterrows():

    doc.append(f"## {row.emoji} {row.theme.title()}")
    doc.append(f"")
    doc.append(f"{row.description}")

markdown = "\n".join(doc)
print(markdown)

with open(f_markdown, "w") as FOUT:
    FOUT.write(markdown)
