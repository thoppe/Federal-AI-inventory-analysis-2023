import pandas as pd
import numpy as np
import textwrap
import json
import argparse
from src import ChatGPT, Schema, tokenized_sampler


f_json = "data/GPT_automated_analysis.json"

with open(f_json) as FIN:
    js = json.load(FIN)

df = pd.DataFrame(js["record_content"])

NUM_QUERY_THREADS = 1
GPT = ChatGPT(cache="cache", max_tokens=1, parallel_threads=NUM_QUERY_THREADS)

for text in df["LLM_summary_text"]:
    v = GPT.embed(text)
    print(v)
    exit()

df["LLM_summary_text"].apply(GPT.embed)
