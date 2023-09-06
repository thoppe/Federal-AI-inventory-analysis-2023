import pandas as pd
import time
import requests
import re
import tiktoken
import os

sleep_time = 10
requests.adapters.DEFAULT_RETRIES = 4

key_name = "OPENAI_API_KEY"

API_KEY = os.environ.get(key_name)
if API_KEY is None:
    print(f"Set {key_name} in as an ENV variable")
    exit(1)


def embed(text):
    query_url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-type": "application/json",
    }
    base_params = {
        "model": "text-embedding-ada-002",
        "input": text,
    }

    params = base_params.copy()
    r = requests.post(query_url, headers=headers, json=params)

    assert r.ok

    result = r.json()
    return result


def query(messages, temperature=0.7, max_tokens=200, n=1):
    query_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-type": "application/json",
    }
    base_params = {
        "model": "gpt-3.5-turbo",
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
        "n": n,
    }

    params = base_params.copy()
    r = requests.post(query_url, headers=headers, json=params)

    if not r.ok:
        print(r.status_code, r.content)
        if r.status_code == 429:
            print(f"Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
            return query(messages, temperature, max_tokens, n)
        else:
            exit()

    result = r.json()

    return result


def recover_list_from_pattern(text, pattern):
    lines = text.split("\n")
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(pattern, line)

        if match:
            item = match.group(1).strip()
            result.append(item)

    return result


##########################################################################

list_type_patterns = {
    "markdown_dash": r"-\s*(.*)",
    "markdown_plus": r"\+\s*(.*)",
    "fancy_bullet": r"•\s*(.*)",
    "numbered_with_period": r"\d+\.\s(.+)",
}


def recover_list_from_response(content):
    target = []
    for k, v in list_type_patterns.items():
        x = recover_list_from_pattern(content, v)
        if len(x) > len(target):
            target = x
    return target


##########################################################################


# Count the tokens
encoding = tiktoken.get_encoding("cl100k_base")


def tokenized_sampler(list_of_strings, query_tokens, seed=7142):
    df = pd.DataFrame(data=list_of_strings, columns=["text"])

    df["n_tokens"] = df["text"].apply(encoding.encode).apply(len)
    df["cum_n_tokens"] = df["n_tokens"].cumsum()
    df["batch_n"] = (df["cum_n_tokens"] + 2) // query_tokens

    batches = []

    for n, dx in df.groupby("batch_n"):
        # Last batch is too small fill it up with a random sample
        if n == df.batch_n.max():
            dx = pd.concat([dx, df[df.batch_n != n].sample(frac=1, random_state=seed)])
            dx["cum_n_tokens"] = dx["n_tokens"].cumsum()
            dx["batch_n"] = (dx["cum_n_tokens"] + 2) // query_tokens
            dx = dx[dx.batch_n == 0]

        batches.append(dx["text"].tolist())

    return batches
