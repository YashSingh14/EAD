import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.vector_store import search_similar_decisions
from utils.db import get_decisions_by_ids

def generate_recommendation(query: str) -> tuple[str, list]:
    """
    Given a user query, performs a similarity search to find historical cases,
    retrieves their full context from the database, and uses an LLM to generate
    an actionable recommendation.
    """
    # 1. Search vector DB for similar cases
    matches = search_similar_decisions(query, top_k=3)
    
    if not matches:
        return "No similar historical cases found in Organizational Memory. You might need to evaluate this as a net-new problem.", []
        
    decision_ids = [match['metadata']['decision_id'] for match in matches]
    
    # 2. Fetch full details from Supabase
    historical_cases_raw = get_decisions_by_ids(decision_ids)
    
    if not historical_cases_raw:
        return "Similar cases were found in the index, but details could not be retrieved from the database.", []
        
    # Reorder cases to match the similarity ranking from Pinecone
    cases_dict = {str(case['id']): case for case in historical_cases_raw}
    historical_cases = [cases_dict[str(d_id)] for d_id in decision_ids if str(d_id) in cases_dict]
        
    # 3. Format historical context for the LLM
    context_str = ""
    for i, case in enumerate(historical_cases):
        context_str += f"--- Historical Case {i+1} ---\n"
        context_str += f"Problem: {case.get('problem_description', 'N/A')}\n"
        context_str += f"Context: {case.get('context', 'N/A')}\n"
        context_str += f"Decision Taken: {case.get('decision_taken', 'N/A')}\n"
        context_str += f"Reasoning: {case.get('reasoning', 'N/A')}\n"
        context_str += f"Outcome: {case.get('outcome', 'N/A')}\n\n"
        
    # 4. Synthesize recommendation using LLM
    if not os.environ.get("OPENAI_API_KEY"):
        raise Exception("OPENAI_API_KEY is not set.")
        
    llm = ChatOpenAI(model="openai/gpt-4o", temperature=0.2, max_tokens=2000)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the EchoMind AI Recommendation Engine. Your task is to analyze a new problem based on historical organizational memory. "
                   "Provide a direct, actionable recommendation for the user. Summarize the similarities from the past cases, explain the risks or success rates based on historical outcomes, "
                   "and give a clear step-by-step recommendation based on how senior experts previously solved it."),
        ("user", "Current Problem: {query}\n\nHistorical Context:\n{context_str}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"query": query, "context_str": context_str})
    
    return response.content, historical_cases
