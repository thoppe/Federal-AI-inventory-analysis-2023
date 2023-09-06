import pandas as pd
import numpy as np
import textwrap
import json
import argparse
from cache_GPT import ChatGPT
from schema import Schema
from utils import tokenized_sampler

f_schema = "src/schema.yaml"
f_csv = "data/record_level_information_FedAI_2023.csv"

f_json = "data/GPT_automated_analysis.json"
is_verbose = True

###########################################################################

random_seed = 43
query_tokens = 2500
n_sample = None
NUM_QUERY_THREADS = 4
max_string_length = 2600

cache = "cache"

GPT_MAX_TOKEN_LENGTH = 4098
max_tokens = GPT_MAX_TOKEN_LENGTH - query_tokens - 300
GPT = ChatGPT(cache=cache, max_tokens=max_tokens, parallel_threads=NUM_QUERY_THREADS)
GPT.verbose = is_verbose


schema = Schema(f_schema)

##################################################################
# Load and preprocess the data

df = pd.read_csv(f_csv)
titles = df["Title"].str.strip().str.strip(".")
df["project_title_text"] = df["Title"] + ": \n" + df["Summary"]
text_col_key = "project_title_text"

# Shuffle the dataset for max diversity of topics
df = df.sample(frac=1.0, random_state=random_seed)


# Keep only unique entries
duplicated_idx = df.duplicated(subset=text_col_key, keep="first")
df = df[~duplicated_idx]

# Take only a non-empty data
org_text = df[text_col_key].str.strip().dropna()
org_text = org_text.str.replace("\n", " ").unique()

assert len(df) == len(org_text)


# For now, keep only a limited subset if requested
# if n_sample is not None:
#    org_text = org_text[:n_sample]

line_lengths = sorted(list(map(len, org_text)))
print("Five longest responses", line_lengths[-5:])
print(f"Max response length set {max_string_length}")

"""
# Truncate long strings
org_text = [
    textwrap.shorten(line, width=max_string_length - 3, placeholder="...")
    for line in org_text
]
line_lengths = list(map(len, org_text))
assert all(len(x) < max_string_length for x in org_text)
"""

assert all(len(x) < max_string_length for x in org_text)

print(f"Evaluating {len(org_text)} responses")
text = org_text

################################################################################
# Clean the strings with AI

# Fix typos and other simple errors
# if "clean_typos" in workflow:
#    text = GPT.multiASK(schema["clean_typos"], response=text)

# Clean biolerplate if needed
# if "clean_boilerplate" in workflow:
#    text = GPT.multiASK(schema["clean_boilerplate"], response=text)

# Shorten the text by summary if needed
text = GPT.multiASK(schema["summarize_response"], response=text)


df["summary_text"] = text

################################################################################
# Process the themes in stages


def chunked_list_response(text, major_query, minor_query):
    # Block the text into chunks and figure out themes for each one
    text_chunks = tokenized_sampler(text, query_tokens)

    themes = GPT.multiASK(
        major_query,
        "list",
        flatten=True,
        multi_response_chunk=text_chunks,
    )

    # Repeat the theme reduction until we get a single list
    while len(tokenized_sampler(themes, query_tokens)) > 1:
        raise ValueError("Untested!")
        theme_chunks = tokenized_sampler(themes, query_tokens)
        themes = GPT.multiASK(major_query, "list", themes=theme_chunks)

        # Combine the themes if we have more than one text chunk
    if len(text_chunks) > 1:
        themes = GPT.multiASK(minor_query, "list", themes=[themes])[0]

    # Clean themes to remove trailing punc
    themes = [x.rstrip(".?!") for x in themes]
    return themes


# Get a description for Department's efforts
dept_df = []

for dept, dx in df.groupby("Department"):
    subset = dx["summary_text"].values

    # This doesn't work as well, better if we mush them all together!
    """
    department = [dept,]*len(subset)
    resp = GPT.multiASK(
        schema["describe_dept"],
        "list",
        department=department,
        responses=subset,
    )
    """

    text_chunks = tokenized_sampler(subset, query_tokens)
    department = [
        dept,
    ] * len(text_chunks)

    # print(dept, len(text_chunks))
    resp = GPT.multiASK(
        schema["describe_dept"], "list", department=department, responses=text_chunks
    )
    bullets = [item for sublist in resp for item in sublist]

    # print(dept, len(resp), len(text_chunks), len(bullets))
    for bullet in bullets:
        dept_df.append({"Department": dept, "highlight": bullet})
dept_df = pd.DataFrame(dept_df)

print(dept_df)
exit()

################################################################################

"""
# Determine the specific AI modalities
modalities = chunked_list_response(
    text,
    schema["major_modality"],
    schema["group_themes"])

#modalities = list(set(modalities))
print(modalities)
"""
################################################################################


themes = chunked_list_response(text, schema["major_themes"], schema["group_themes_12"])
print(themes)

human_themes = [
    "healthcare",
    "spatial",
    "wildfire",
    "maritime",
    "cyber intelligence",
    "security",
    "environmental",
    "customer service or engagement",
    "power systems",
    "infrastructure",
    "fraud",
]

themes = human_themes
print(themes)

# Measure each response across the themes
theme_str = "\n".join(f"- {x}" for x in themes)
prompt = schema["measure_themes"].format(themes=theme_str, response="{response}")

successful_run = False

while not successful_run:
    successful_run = True

    # Run the score function
    scores = GPT.multiASK(prompt, "json", response=text)

    # Check if all keys in themes, if not need to write code to rerun/invalidate
    for item in scores:
        for key in item:
            if key not in themes:
                print(key, themes)
                assert key in themes

# Convert to a dataframe and sort by most popular themes
sf = pd.json_normalize(scores, meta=themes, errors="raise")
top_themes = sf.describe().T["mean"].sort_values(ascending=False)
print(top_themes)

ms = sf.copy()
ms = ms.replace(to_replace=ms.values, value="")

for theme in sf.columns:
    # Gather the subset that match the theme
    idx = sf[theme] == True

    text_subset = np.array(text)[idx]
    matching_text = GPT.multiASK(
        schema["explain_score"],
        theme=[theme] * len(text_subset),
        response=text_subset,
    )

    # Remove quotes
    matching_text = [x.strip('"').strip("'") for x in matching_text]

    ms.loc[idx, theme] = matching_text
    ms.loc[~idx, theme] = "None"

idx = (
    ms.applymap(lambda x: "None" in x)
    | ms.applymap(lambda x: "not relevant" in x.lower())
    | ms.applymap(lambda x: "not mention" in x.lower())
)

# Revise the scores so we only keep those that have been found "relevant"
sf[:] = (~idx).astype(int)
top_themes = sf.describe().T["mean"].sort_values(ascending=False)


top_themes = top_themes.index.values

# Get a description for each theme
text = np.array(text)
samples = []
for theme in themes:
    # Get a random sample of the text
    tx = text[sf[theme] == True]
    tx = tokenized_sampler(tx, query_tokens)[0]  # Keep only one chunk
    tx = tx[::2]  # Only keep half
    samples.append(tx)

desc = GPT.multiASK(schema["describe_theme"], theme=themes, responses=samples)

# Generate an executive summary
desc_text = "\n".join(desc)
exec_sum = GPT.multiASK(
    schema["executive_summary"], "text", all_theme_desc=[desc_text]
)[0]

# Generation actionable steps for each theme
actionable_steps = GPT.multiASK(
    schema["actionable_steps"], "list", theme_description=desc
)

# Generate some synthetic responses
# synth = GPT.multiASK(
#    schema["synthetic_responses"], "list", theme=themes, responses=samples
# )
# synth = [[x.strip('"') for x in z] for z in synth]


# Find the best matches
matches = GPT.multiASK(
    schema["sample_responses"], "list", theme=themes, responses=samples
)
matches = [[x.strip('"') for x in z] for z in matches]

# Get a keyword for each theme
keywords = GPT.multiASK(schema["keyword_themes"], theme=themes, desc=desc)
keywords = [x.strip(" .").title() for x in keywords]

print(keywords)

# Get an emoji for each theme
emoji = GPT.multiASK(schema["emoji_themes"], theme=themes, desc=desc)
print(emoji)

# Convert the data into a useful format for export
dx = pd.DataFrame()
dx["theme"] = themes
dx["emoji"] = emoji
# dx["synthetic_responses"] = synth
dx["real_responses"] = matches
dx["description"] = desc
dx["actionable_steps"] = actionable_steps
dx["total_observations"] = len(df)
dx["positive_observations"] = sf.sum(axis=0).values
dx = dx.sort_values("positive_observations", ascending=False)
data = dx.to_json(orient="records", indent=2)

# Add record level data
df["LLM_summary_text"] = text.tolist()

# print(data)
print(dx.set_index("emoji")[["theme", "positive_observations"]])

# Save the usage statistics
js = {
    "theme_content": json.loads(data),
    "record_content": json.loads(df.to_json()),
    "department_content": json.loads(dept_df.to_json()),
}

js["meta"] = {
    "cost": GPT.total_cost,
    "tokens": GPT.total_tokens,
    "calls": GPT.total_API_calls,
}


js["explainations"] = ms.to_json()

# Save the global observations
js["executive_summary"] = exec_sum
# js["actionable_steps"] = actionable_steps

# save_dest = Path("results")
# save_dest.mkdir(exist_ok=True)
# f_save = save_dest / f_csv.with_suffix(".json").name

with open(f_json, "w") as FOUT:
    FOUT.write(json.dumps(js, indent=2))

print(GPT)
