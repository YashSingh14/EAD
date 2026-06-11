import os
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
import tempfile

class DecisionData(BaseModel):
    problem_description: str = Field(description="The core problem, incident, or situation being solved")
    context: str = Field(description="Background information, environmental factors, and data constraints at the time")
    options_considered: str = Field(description="Alternative options or solutions that were evaluated")
    decision_taken: str = Field(description="The final action or path chosen")
    reasoning: str = Field(description="Why this specific path was chosen over the alternatives (expert intuition, rules, etc.)")
    outcome: str = Field(description="The final result, impact, or lessons learned after the decision was implemented")

def get_extractor_llm():
    if not os.environ.get("OPENAI_API_KEY"):
        raise Exception("OPENAI_API_KEY is not set.")
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm.with_structured_output(DecisionData)

def extract_decision_from_text(text: str) -> dict:
    """
    Uses an LLM to extract structured decision data from unstructured text.
    """
    structured_llm = get_extractor_llm()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the EchoMind AI Reasoning Extractor. Your job is to read meeting notes, incident reports, post-mortems, or general text and extract the organizational knowledge into the EchoMind Decision Framework. Ensure all fields are captured accurately. If a specific field is not explicitly mentioned, try to infer it logically from the context, or provide a brief summary of what is known."),
        ("user", "{text}")
    ])
    
    chain = prompt | structured_llm
    result = chain.invoke({"text": text})
    return result.dict()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Saves bytes to a temp file, extracts text using PyPDFLoader, and cleans up.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        full_text = "\\n".join([page.page_content for page in pages])
        return full_text
    finally:
        os.remove(tmp_path)
