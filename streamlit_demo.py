import json
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import umap
from sklearn.cluster import DBSCAN, MiniBatchKMeans
import viz_interface as interface
from bokeh.models import Label
import yake
import datetime
from sklearn.decomposition import PCA, IncrementalPCA

start_time = datetime.datetime.now()

threshold_cutoff = 0.30

st.set_page_config(layout="wide")
st.title("Federal AI inventory analysis 2022")

@st.cache_data
def load_vectors(f_npy, n_dim = 40):
    # Loads in the vectors and highly compress them via SVD
    ipca = IncrementalPCA(n_components=n_dim)
    V = np.load(f_npy)
    
    Vt = ipca.fit_transform(V)
    return Vt

@st.cache_data
def umap_vectors(V):
    # Compress data down to two dimensions for visualization
    clf = umap.UMAP(n_neighbors=5, random_state=44, min_dist=0.055)
    X = clf.fit(V)

    embedding = clf.embedding_.copy()
    embedding -= embedding.mean(axis=0)
    embedding /= embedding.std(axis=0)
    
    return embedding

@st.cache_data
def cluster_data(embedding, num_text_labels=25):
    clf = MiniBatchKMeans(n_clusters=num_text_labels, batch_size=1000)
    return clf.fit_predict(embedding)

@st.cache_data
def compute_keywords(df, num_text_labels=25):

    clusters = df.cluster.unique()
    
    output = {}

    for col in clusters:
        dx = df[df.cluster == col]
        dx = dx.reset_index()
        
        custom_kw_extractor = yake.KeywordExtractor(
            lan='en', n=3, dedupLim=0.9, top=5, features=None)

        text = '\n'.join([title for title in dx['Summary'].tolist()])
        
        keywords = [kw[0] for kw in custom_kw_extractor.extract_keywords(text)]
        keywords = [kw for kw in keywords
                    if 'machine' not in kw.lower()
                    and 'main idea' not in kw.lower()
                    and 'data' not in kw.lower()
                    and 'learning' not in kw.lower()
                    and 'model' not in kw.lower()
                    and 'system' not in kw.lower()
                    and 'intelligence' not in kw.lower()
                    and 'artificial' not in kw.lower()
        ]

        if not keywords:
            top_phrase = ''
        else:
            top_phrase = keywords[0]
        
        output[col] = top_phrase
    return output



f_npy = 'data/GPT_embedding.npy'
V = load_vectors(f_npy)

embedding = umap_vectors(V)

f_json = 'data/GPT_automated_analysis.json'

with open(f_json) as FIN:
    js = json.load(FIN)
df = pd.DataFrame(js["record_content"])

#df = load_csv(f_csv)
df = df.copy()

df['ux'], df['uy'] = embedding.T

bool_overlay_text = st.sidebar.checkbox("Overlay text", True)
n_text_show = st.sidebar.slider('Number of overlay text', 0, 50, 10)
#bool_show_citations = st.sidebar.checkbox("Show citations", True)

if n_text_show > 0:
    df['cluster'] = cluster_data(embedding, n_text_show)
    keywords = compute_keywords(df, n_text_show)


dept_opt = df.groupby("Department").size().sort_values(ascending=False).index.tolist()
dept_opt = ["None"] + dept_opt
highlight_department = st.sidebar.selectbox('Highlight Dept/Agency', dept_opt)
   
df["line_width"] = 0
df["color"] = "#3288bd"
df["fill_color"] = df["color"]
df['no_focus'] = 1

colors = ["#05baae", "#b4ef86", "#e47474", "#e4749c"] * 1000
expand = 2.0
point_size = .04

df["size"] = point_size
df["alpha"] = .35

# Custom coloring
idx = df["Department"] == highlight_department
if idx.sum():
    st.write(f"Highlighting {idx.sum()} projects from {highlight_department}")

df.loc[idx, 'fill_color'] = colors[2]
df.loc[idx, 'size'] = point_size*expand
df.loc[idx, 'line_width'] = 5

viz_cols = [
    "Title",
    "Department",
    #"LLM_summary_text",
    "Summary",
]

p = interface.plot_data_bokeh(df, hover_columns=viz_cols, tooltips=True)
plot_placeholder = st.empty()


if n_text_show > 0:

    clusters = df.cluster.unique()
    
    for col in clusters:
        dx = df[df.cluster == col]
        dx = dx.reset_index()

        cmx, cmy = dx.ux.mean(), dx.uy.mean()

        if not len(dx):
            continue
        
        dx['dist'] = (dx['ux'] - cmx)**2 + (dx['uy'] - cmy)**2
        dx = dx.sort_values('dist')

        top_phrase = keywords[col]
        
        label_args = {
            "x": cmx,
            "y": cmy,
            "text": top_phrase,
            "text_color": "black",
            "background_fill_color": "white",
            "background_fill_alpha": 0.25,
        }

        if bool_overlay_text:
            p.add_layout(Label(**label_args))
        

end_time = datetime.datetime.now()
dt = (end_time-start_time).total_seconds()
st.sidebar.write(f"Compute time {dt:0.3f}")

save_btn = st.sidebar.button("Export HTML Plot")

f_save = Path(f'results/vizmap.html')
f_save.parent.mkdir(exist_ok=True)

if save_btn:  
    import bokeh
    from bokeh.plotting import figure, output_file, show
    bokeh.io.output_file(f_save, "Fed_AI_2022")
    show(p)
    st.write(f_save)

else:
    st.bokeh_chart(p)
    st.write(f_save)

