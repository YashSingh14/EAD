import sys
import os
import tempfile
import streamlit as st

# Ensure root directory is in the Python path for local module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingest.ingestion import DocumentIngestionPipeline
from data.vector_store import LocalVectorStore
from core.orchestration import HybridLLMOrchestrator
from export.document_generators import generate_pdf_buffer, generate_docx_buffer

# ---------------------------------------------------------
# Application Initialization & State Management
# ---------------------------------------------------------

st.set_page_config(
    page_title="Enterprise AI RAG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. State Management and Conversational Memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "vector_store" not in st.session_state:
    st.session_state.vector_store = LocalVectorStore()
    
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = None

if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

# Initialize the ingestion pipeline (cached so we don't recreate the chunker repeatedly)
@st.cache_resource
def get_ingestion_pipeline():
    return DocumentIngestionPipeline(chunk_size=1000, chunk_overlap=200)

ingestion_pipeline = get_ingestion_pipeline()

# ---------------------------------------------------------
# 1. Dual-Column Layout: Sidebar Configuration Panel
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # LLM Backend Toggle
    llm_provider = st.selectbox(
        "Select LLM Pathway:",
        options=["Local-First (Air-Gapped)", "Cloud-Accelerated (Free Tier)"],
        index=0
    )
    provider_key = "local" if "Local" in llm_provider else "cloud"
    
    model_name = st.text_input(
        "Model Name", 
        value="mistral" if provider_key == "local" else "gemini-1.5-flash",
        help="Specify 'mistral', 'llama3' for local, or 'gemini-1.5-flash' for Google Cloud."
    )
    
    if st.button("Apply Engine Configuration"):
        with st.spinner("Connecting to LLM engine..."):
            try:
                st.session_state.orchestrator = HybridLLMOrchestrator(
                    vector_store=st.session_state.vector_store,
                    provider=provider_key,
                    model_name=model_name
                )
                st.success("Engine successfully configured!")
            except Exception as e:
                st.error(f"Failed to initialize engine: {e}")

    st.divider()
    
    st.header("📄 Document Ingestion")
    # File Uploader
    uploaded_files = st.file_uploader(
        "Upload Documents for Semantic Context", 
        type=["pdf", "docx", "txt", "html", "htm"], 
        accept_multiple_files=True
    )
    
    # 3. Reactive Ingestion Trigger & Automated Vector Space Reset
    if uploaded_files:
        current_file_names = {f.name for f in uploaded_files}
        
        # If the set of files in the uploader has changed
        if current_file_names != st.session_state.processed_files:
            with st.spinner("Processing new document set & wiping old vector space..."):
                # Reset state to prevent semantic cross-contamination
                st.session_state.vector_store.reset_state()
                st.session_state.processed_files.clear()
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    all_chunks = []
                    for uploaded_file in uploaded_files:
                        temp_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        # Parse and semantically chunk
                        chunks = ingestion_pipeline.process_document(temp_path)
                        all_chunks.extend(chunks)
                        st.session_state.processed_files.add(uploaded_file.name)
                    
                    # Embed and Store in ChromaDB
                    if all_chunks:
                        st.session_state.vector_store.ingest_chunks(all_chunks)
                        st.success(f"Indexed {len(all_chunks)} semantic chunks successfully!")
                    else:
                        st.warning("No readable text could be extracted from these documents.")
    
    # Handle the scenario where the user removes all files from the uploader
    elif len(st.session_state.processed_files) > 0:
        st.session_state.vector_store.reset_state()
        st.session_state.processed_files.clear()
        st.info("All documents removed. Vector space has been wiped clean.")

    st.divider()
    if st.button("Clear Chat History", type="secondary"):
        st.session_state.messages = []
        st.rerun()

def render_citations(sources):
    if not sources:
        return
    with st.expander("🔍 View Source Citations"):
        grouped_sources = {}
        for doc in sources:
            filename = doc.metadata.get('filename', 'Unknown Source')
            page = doc.metadata.get('page_number', 'N/A')
            key = (filename, page)
            if key not in grouped_sources:
                grouped_sources[key] = []
            grouped_sources[key].append(doc.page_content)
            
        for (filename, page), chunks in grouped_sources.items():
            st.markdown(f"**Source Document:** **{filename}**  \n**Location:** Page {page}")
            for chunk in chunks:
                clean_chunk = chunk.replace('\n', '\n> ')
                st.markdown(f"> {clean_chunk}")
            st.divider()

def render_download_buttons(content: str, index: int):
    if not content or len(content) < 10:
        return
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        st.download_button(
            label="📄 Export PDF",
            data=generate_pdf_buffer(content).getvalue(),
            file_name=f"AI_Insight_{index}.pdf",
            mime="application/pdf",
            key=f"pdf_btn_{index}"
        )
    with col2:
        st.download_button(
            label="📝 Export DOCX",
            data=generate_docx_buffer(content).getvalue(),
            file_name=f"AI_Insight_{index}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"docx_btn_{index}"
        )

# ---------------------------------------------------------
# 1. Dual-Column Layout: Main Chat Interface
# ---------------------------------------------------------
st.title("Enterprise Hybrid RAG Interface")
st.markdown("Query your uploaded documents securely. Hallucinations are actively suppressed.")

# Initialize default orchestrator if one hasn't been set yet
if st.session_state.orchestrator is None:
    st.session_state.orchestrator = HybridLLMOrchestrator(
        vector_store=st.session_state.vector_store,
        provider="local",
        model_name="mistral"
    )

# Render Chat History from Memory
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            render_citations(message["sources"])
        if message["role"] == "assistant":
            render_download_buttons(message["content"], i)

# User Chat Input
if prompt := st.chat_input("Ask a question based strictly on the uploaded documents..."):
    # Append to memory state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Format historical context to maintain conversational momentum
    history_string = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}" 
        for m in st.session_state.messages[:-1] # Exclude the current prompt
    ])

    with st.chat_message("assistant"):
        with st.spinner("Analyzing semantic vectors and applying reasoning..."):
            try:
                # Execute Hybrid RAG Pipeline
                response_data = st.session_state.orchestrator.generate_response(
                    query=prompt, 
                    chat_history=history_string
                )
                
                answer = response_data["answer"]
                sources = response_data["source_documents"]
                
                # Display output stream
                st.markdown(answer)
                
                # Expandable Semantic Attributions with Deduplication
                render_citations(sources)
                
                # Render In-Memory Export Buttons for the new response
                new_msg_index = len(st.session_state.messages)
                render_download_buttons(answer, new_msg_index)
                            
                # Commit agent response to memory state with citations
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": sources
                })
                
            except Exception as e:
                error_msg = f"System Error during LLM reasoning execution: {e}"
                st.error(error_msg)
                logger.error(error_msg)
