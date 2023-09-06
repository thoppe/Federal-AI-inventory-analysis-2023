import numpy as np
from tqdm import tqdm
import pandas as pd
import json
from cache_GPT import ChatGPT

f_json = "data/GPT_automated_analysis.json"
f_npy = "data/GPT_embedding.npy"

with open(f_json) as FIN:
    js = json.load(FIN)

df = pd.DataFrame(js["record_content"])

NUM_QUERY_THREADS = 1
GPT = ChatGPT(cache="cache", max_tokens=1, parallel_threads=NUM_QUERY_THREADS)

V = [GPT.embed(text) for text in tqdm(df["LLM_summary_text"])]
V = np.array(V)

np.save(f_npy, V)
