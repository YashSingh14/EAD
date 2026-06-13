import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    logging.warning("Supabase credentials are not fully set in the environment variables.")
    supabase = None
else:
    supabase: Client = create_client(url, key)

def insert_decision(data: dict) -> dict:
    """
    Inserts a new decision record into the Supabase database.
    Returns the inserted data.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
    
    response = supabase.table("decisions").insert(data).execute()
    if response.data:
        return response.data[0]
    return {}

def update_decision_vector_id(decision_id: str, vector_id: str):
    """
    Updates the vector_id for a given decision.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    response = supabase.table("decisions").update({"vector_id": vector_id}).eq("id", decision_id).execute()
    return response.data

def get_decision_by_id(decision_id: str) -> dict:
    """
    Retrieves a decision by its ID.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    response = supabase.table("decisions").select("*").eq("id", decision_id).execute()
    if response.data:
        return response.data[0]
    return {}

def get_decisions_by_ids(decision_ids: list) -> list:
    """
    Retrieves multiple decisions by their IDs.
    """
    if not supabase:
        raise Exception("Supabase client is not initialized.")
        
    response = supabase.table("decisions").select("*").in_("id", decision_ids).execute()
    return response.data
