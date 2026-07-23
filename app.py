import os
import streamlit as st
import numpy as np
import traceback
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

from src.extract import extract_text_from_file
from src.chunk import chunk_text
from src.embed import EmbeddingManager
from src.retrieve import retrieve_top_k
from src.generate import generate_answer

print("=" * 50)
print("APP.PY LOADED")
print(__file__)
print("=" * 50)

st.set_page_config(
    page_title="FAQ Bot - Single Document RAG",
    page_icon="🤖",
    layout="wide"
)

if "embedding_manager" not in st.session_state:
    st.session_state.embedding_manager = None

if "document_data" not in st.session_state:
    st.session_state.document_data = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ---------------- SIDEBAR ----------------
st.sidebar.title("🤖 FAQ Bot Configuration")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "Upload Document (PDF or TXT)",
    type=["pdf", "txt"],
    help="Upload a document to index and query."
)

st.sidebar.markdown("### ⚙️ RAG Hyperparameters")
threshold = st.sidebar.slider(
    "Similarity Threshold",
    min_value=0.0,
    max_value=1.0,
    value=float(os.getenv("SIMILARITY_THRESHOLD", 0.25)),
    step=0.05
)

top_k = st.sidebar.slider(
    "Top-K Chunks to Retrieve",
    min_value=1,
    max_value=10,
    value=int(os.getenv("TOP_K", 3)),
    step=1
)

st.sidebar.markdown("### 🔑 LLM API Settings")
provider = st.sidebar.selectbox(
    "LLM Provider",
    options=["auto", "gemini", "openai","groq","mock"],
    index=0
)

api_key_input = st.sidebar.text_input(
    "API Key (Optional override)",
    type="password"
)

if api_key_input:
    if provider == "openai":
        os.environ["OPENAI_API_KEY"] = api_key_input
    elif provider == "groq":
        os.environ["GROQ_API_KEY"] = api_key_input
    else:
        os.environ["GEMINI_API_KEY"] = api_key_input

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Session & History", use_container_width=True):
    st.session_state.document_data = None
    st.session_state.chat_history = []
    st.rerun()

# ---------------- CORE LOGIC ----------------
if uploaded_file is not None:
    current_filename = uploaded_file.name
    if (
        st.session_state.document_data is None or
        st.session_state.document_data["filename"] != current_filename
    ):
        with st.spinner(f"Extracting & Indexing '{current_filename}'..."):
            try:
                document = extract_text_from_file(uploaded_file, current_filename)
                
                raw_text = document["text"]
                pages = document["pages"]
                
                chunk_size = int(os.getenv("CHUNK_SIZE", 250))
                overlap = int(os.getenv("CHUNK_OVERLAP", 50))
                chunks = chunk_text(pages, chunk_size=chunk_size, overlap=overlap)
                
                if st.session_state.embedding_manager is None:
                    st.session_state.embedding_manager = EmbeddingManager()
                
                embeddings = st.session_state.embedding_manager.fit_and_embed_chunks(chunks)

                st.session_state.document_data = {
                    "filename": current_filename,
                    "text": raw_text,
                    "pages": pages,
                    "chunks": chunks,
                    "embeddings": embeddings
                }
                st.session_state.chat_history = []
                st.toast(f"Successfully indexed {len(chunks)} chunks!", icon="✅")
            except Exception as e:
                st.exception(e)
                traceback.print_exc()

# ---------------- MAIN DASHBOARD ----------------
st.title("📚 Single-Document FAQ Assistant")
st.markdown("Ask natural language questions about your uploaded document.")

doc = st.session_state.document_data

if doc is None:
    st.info("👈 Please upload a PDF or TXT file using the sidebar to begin.")
    
    if st.button("📄 Or click here to load the Sample Policy Document"):
        sample_path = "data/sample_docs/sample_policy.txt"
        if os.path.exists(sample_path):
            with open(sample_path, "r") as f:
                content = f.read()
            chunks = chunk_text(content, chunk_size=250, overlap=50)
            if st.session_state.embedding_manager is None:
                st.session_state.embedding_manager = EmbeddingManager()
            embeddings = st.session_state.embedding_manager.fit_and_embed_chunks(chunks)
            
            st.session_state.document_data = {
                "filename": "sample_policy.txt",
                "text": content,
                "chunks": chunks,
                "embeddings": embeddings
            }
            st.rerun()
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Indexed Document", doc["filename"])
    col2.metric("Total Character Count", f"{len(doc['text']):,}")
    col3.metric("Indexed Chunks", f"{len(doc['chunks'])}")
    
    st.markdown("---")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "retrieved_results" in message and message["retrieved_results"]:
                with st.expander("🔍 View Retrieved Source Chunks"):
                    for item in message["retrieved_results"]:
                        st.write("🚀 TEST SUCCESS")
                        c = item["chunk"]
                        st.write(c)
                        score = item["score"]
                        st.markdown("### 📄 Source Information")

                        st.write(f"**📘 Document:** {doc['filename']}")
                        st.write(f"**📄 Page Number:** {c.get('page', 'Not Available')}")
                        st.write(f"**🧩 Chunk ID:** {c['id']}")
                        st.progress(min(score, 1.0))
                        st.write(f"**📊 Similarity Score:** {score:.4f}")
                        st.markdown("**📄 Retrieved Text:**")
                        st.caption(c["text"])

                        st.divider()
                        

    if user_question := st.chat_input("Ask a question about the document..."):

    # Save user message
        st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_question
        }
    )

        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):

            with st.spinner("Retrieving relevant context & generating grounded answer..."):

                # Default search query
                search_query = user_question.strip()

                # Handle follow-up questions
                if (
                    len(st.session_state.chat_history) >= 2
                    and search_query.lower().startswith(
                        ("it", "this", "that", "explain", "tell", "more", "why", "how")
                    )
                ):

                    previous_user = ""

                    for msg in reversed(st.session_state.chat_history[:-1]):
                        if msg["role"] == "user":
                            previous_user = msg["content"]
                            break

                    if previous_user:
                        search_query = previous_user + " " + search_query

                print("=" * 50)
                print("USER QUESTION :", repr(user_question))
                print("SEARCH QUERY  :", repr(search_query))
                print("=" * 50)

                if search_query.strip() == "":
                    search_query = user_question

                query_vec = st.session_state.embedding_manager.embed_query(search_query)

                retrieval = retrieve_top_k(
                    query_vec=query_vec,
                    chunk_vecs=doc["embeddings"],
                    chunks=doc["chunks"],
                    top_k=top_k,
                    threshold=threshold
                )

                print("=" * 60)
                print("RETRIEVAL RESULTS")
                print(retrieval)
                print("=" * 60)

                print("===== APP CHAT HISTORY =====")
                print(st.session_state.chat_history)
                print("============================")

                answer = generate_answer(
                    query=user_question,
                    retrieved_results=retrieval["results"],
                    is_relevant=retrieval["is_relevant"],
                    provider=provider,
                    chat_history=st.session_state.chat_history
                )

                st.markdown(answer)

                if retrieval["results"]:
                    with st.expander("🔍 View Retrieved Source Chunks"):
                        for item in retrieval["results"]:
                            c = item["chunk"]
                            score = item["score"]

                            st.markdown("### 📄 Source Information")

                            st.write(f"**📘 Document:** {doc['filename']}")

                            st.write(f"**📄 Page Number:** {c['page']}")

                            st.write(f"**🧩 Chunk ID:** {c['id']}")

                            st.progress(min(score, 1.0))

                            st.write(f"**📊 Similarity Score:** {score:.4f}")

                            st.markdown("**📄 Retrieved Text:**")

                            st.caption(c["text"])

                            st.divider()
        # Save assistant response
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": answer,
                "retrieved_results": retrieval["results"]
            }
        )