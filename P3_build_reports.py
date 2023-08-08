import pandas as pd
import json

f_json = "data/GPT_automated_analysis.json"
f_markdown = "results/AI_topics_by_Department.md"

with open(f_json) as FIN:
    js = json.load(FIN)

df = pd.DataFrame(js["department_content"])
df["Department"] = df["Department"].apply(lambda x:x.replace(' ', '_'))

# Sort by most counted
idx = df["Department"].value_counts()
df = df.set_index("Department")  # [idx]
df["dcount"] = idx
df = df.sort_values(["dcount", "Department"], ascending=False)
del df["dcount"]

doc = []
doc.append("# AI topics across Departments")
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
