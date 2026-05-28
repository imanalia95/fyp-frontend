import os
import streamlit as st
from rag_chain import build_rag_chain, run_rag
import chromadb
from sentence_transformers import SentenceTransformer

st.set_page_config(
    page_title="FYP Supervisor Recommender",
    page_icon="🎓",
    layout="centered"
)

@st.cache_resource
def load_resources():
    client     = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection("lecturers")
    model      = SentenceTransformer('all-MiniLM-L6-v2')
    return collection, model

collection, model = load_resources()

st.title("FYP Supervisor Recommender")
st.caption("FCSIT UNIMAS — Match your research interests to a supervisor")
st.divider()

with st.sidebar:
    st.header("Settings")
    top_n = st.slider("Number of recommendations", 1, 10, 5)
    st.divider()
    st.metric("Lecturers in DB", collection.count())

EXAMPLES = [
    "deep learning for medical image classification",
    "blockchain and cybersecurity",
    "natural language processing NLP",
    "IoT smart home systems",
    "mobile app development Android",
    "software engineering formal methods",
]

st.subheader("Try an example")
cols = st.columns(3)
for i, ex in enumerate(EXAMPLES):
    if cols[i % 3].button(ex, use_container_width=True):
        st.session_state['query'] = ex

st.subheader("Describe your research interests")
query = st.text_area(
    label="",
    placeholder="e.g. I'm interested in using deep learning to detect plant diseases from smartphone images...",
    height=120,
    value=st.session_state.get('query', ''),
    key="query_input"
)

search_btn = st.button("🔍 Find Supervisors", type="primary", use_container_width=True)

# ── Search ────────────────────────────────────────────────────────────
if search_btn and query.strip():
    with st.spinner("Finding best matches..."):
        q_vec   = model.encode([query], normalize_embeddings=True).tolist()
        results = collection.query(query_embeddings=q_vec, n_results=top_n)

    st.divider()
    st.subheader(f"Top {top_n} Recommended Supervisors")

    metas = results['metadatas'][0]
    dists = results['distances'][0]

    for i, (meta, dist) in enumerate(zip(metas, dists)):
        sim = round(1 - dist, 4)
        sim_pct = round(sim * 100, 1)

        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        medal  = medals.get(i, f"#{i+1}")

        with st.expander(f"{medal} {meta['name']}  —  {sim_pct}% match", expanded=(i < 3)):
            
            # Image
            if meta.get("img_url"):
                st.image(meta["img_url"], width=150)

            # Similarity bar
            st.progress(sim, text=f"Similarity score: {sim:.4f}")

            # Summary
            if meta['summary']:
                st.markdown(f"**About:** {meta['summary']}")

            # Stats
            col1, col2 = st.columns(2)
            col1.metric("📄 Journal Articles", meta['num_articles'])
            col2.metric("📰 Conference Papers", meta['num_proceedings'])

            # Top publications
            if meta['top_articles']:
                st.markdown("**Recent publications:**")
                for pub in meta['top_articles'].split(';')[:3]:
                    if pub.strip():
                        st.markdown(f"- {pub.strip()}")

            # Google Scholar link
            if meta['google_scholar']:
                st.link_button("View Google Scholar Profile", meta['google_scholar'])

elif search_btn:
    st.warning("Please enter your research interests first.")