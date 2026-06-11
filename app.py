import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables first
load_dotenv()

from utils.db import insert_decision, update_decision_vector_id
from utils.vector_store import add_decision_to_vector_store
from utils.ai_extractor import extract_decision_from_text, extract_text_from_pdf
from utils.recommender import generate_recommendation

st.set_page_config(page_title="EchoMind OS", page_icon="🧠", layout="wide")

# Custom styling for a cleaner look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-top: 0;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">EchoMind</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">The Organizational Memory Operating System</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 Search & Recommend", "📝 Manual Capture", "🤖 AI Upload"])

# --- TAB 1: Search & Recommend ---
with tab1:
    st.header("Similar Case Finder")
    st.write("Query the organizational memory to find how experts solved similar problems.")
    
    query = st.text_input("Describe the problem or symptom you are currently facing...", 
                          placeholder="e.g., Abnormal high-frequency vibration on Conveyor Belt B...")
    
    if st.button("Search Memory", type="primary"):
        if query:
            with st.spinner("Searching organizational memory and synthesizing recommendation..."):
                try:
                    recommendation, cases = generate_recommendation(query)
                    
                    st.subheader("💡 AI Recommendation")
                    st.info(recommendation)
                    
                    if cases:
                        st.subheader("📚 Historical Evidence")
                        for i, case in enumerate(cases):
                            with st.expander(f"Historical Case {i+1}: {str(case.get('problem_description', ''))[:80]}..."):
                                st.markdown(f"**Context:** {case.get('context')}")
                                st.markdown(f"**Decision Taken:** {case.get('decision_taken')}")
                                st.markdown(f"**Reasoning:** {case.get('reasoning')}")
                                st.markdown(f"**Outcome:** {case.get('outcome')}")
                                st.caption(f"Logged on: {case.get('created_at')}")
                except Exception as e:
                    st.error(f"Error connecting to services: {str(e)}")
        else:
            st.warning("Please enter a problem description to search.")

# --- TAB 2: Manual Capture ---
with tab2:
    st.header("Capture Expert Decision")
    st.write("Manually log an important decision to preserve the reasoning behind it.")
    
    with st.form("capture_form"):
        problem = st.text_area("Problem Description *", help="What was the core problem or situation?", height=100)
        context = st.text_area("Context & Constraints", help="What was the environment or business constraints at the time?", height=100)
        options = st.text_area("Options Considered", help="What else did you evaluate and why was it rejected?", height=100)
        decision = st.text_area("Decision Taken *", help="What specific action did you take?", height=100)
        reasoning = st.text_area("Reasoning / Intuition *", help="Why did you choose this path? Share your expert intuition.", height=150)
        outcome = st.text_area("Outcome / Lessons Learned", help="What was the result of this decision?", height=100)
        
        st.markdown("*Required fields")
        submitted = st.form_submit_button("Log Decision to EchoMind", type="primary")
        
        if submitted:
            if not problem or not decision or not reasoning:
                st.error("Please fill in the required fields: Problem, Decision, and Reasoning.")
            else:
                with st.spinner("Saving and embedding into vector store..."):
                    try:
                        data = {
                            "problem_description": problem,
                            "context": context,
                            "options_considered": options,
                            "decision_taken": decision,
                            "reasoning": reasoning,
                            "outcome": outcome,
                            "status": "manual_entry"
                        }
                        
                        # 1. Insert to Supabase DB
                        inserted = insert_decision(data)
                        decision_id = inserted.get("id")
                        
                        if decision_id:
                            # 2. Embed and save to Pinecone Vector DB
                            vector_id = add_decision_to_vector_store(decision_id, problem, decision)
                            # 3. Update DB with vector_id link
                            update_decision_vector_id(decision_id, vector_id)
                            
                            st.success("✅ Successfully captured and embedded into Organizational Memory!")
                        else:
                            st.error("Failed to insert decision into the database.")
                    except Exception as e:
                        st.error(f"Error saving decision: {str(e)}")

# --- TAB 3: AI Reasoning Extractor ---
with tab3:
    st.header("AI Reasoning Extractor")
    st.write("Upload unstructured post-mortems or meeting notes, and let AI structure it into the decision framework.")
    
    uploaded_file = st.file_uploader("Upload Document (.txt, .pdf)", type=['txt', 'pdf'])
    
    if uploaded_file is not None:
        if st.button("Extract Knowledge", type="primary"):
            with st.spinner("Extracting structured decision data using AI..."):
                try:
                    if uploaded_file.name.endswith(".pdf"):
                        text = extract_text_from_pdf(uploaded_file.read())
                    else:
                        text = uploaded_file.read().decode("utf-8")
                        
                    extracted_data = extract_decision_from_text(text)
                    
                    st.success("Extraction Complete! Review the data below before saving to EchoMind.")
                    
                    # Store in session state so user can review and save in next interaction
                    st.session_state['extracted_data'] = extracted_data
                    
                except Exception as e:
                    st.error(f"Error extracting text: {str(e)}")
                    
    # Show extracted data if available in session state
    if 'extracted_data' in st.session_state:
        st.divider()
        st.subheader("Review Extracted Data")
        
        data = st.session_state['extracted_data']
        
        # Display as editable fields? For MVP, just displaying them.
        st.markdown(f"**Problem Description:**<br>{data.get('problem_description')}", unsafe_allow_html=True)
        st.markdown(f"**Context:**<br>{data.get('context')}", unsafe_allow_html=True)
        st.markdown(f"**Options Considered:**<br>{data.get('options_considered')}", unsafe_allow_html=True)
        st.markdown(f"**Decision Taken:**<br>{data.get('decision_taken')}", unsafe_allow_html=True)
        st.markdown(f"**Reasoning:**<br>{data.get('reasoning')}", unsafe_allow_html=True)
        st.markdown(f"**Outcome:**<br>{data.get('outcome')}", unsafe_allow_html=True)
        
        st.write("")
        if st.button("Confirm & Save to EchoMind", type="primary"):
            with st.spinner("Saving to database and vector store..."):
                try:
                    save_data = data.copy()
                    save_data["status"] = "ai_extracted"
                    
                    # 1. Insert to Supabase DB
                    inserted = insert_decision(save_data)
                    decision_id = inserted.get("id")
                    
                    if decision_id:
                        # 2. Embed and save to Pinecone Vector DB
                        vector_id = add_decision_to_vector_store(decision_id, data['problem_description'], data['decision_taken'])
                        update_decision_vector_id(decision_id, vector_id)
                        
                        st.success("✅ Extracted decision successfully saved into Organizational Memory!")
                        # Clear session state
                        del st.session_state['extracted_data']
                except Exception as e:
                    st.error(f"Error saving decision: {str(e)}")
