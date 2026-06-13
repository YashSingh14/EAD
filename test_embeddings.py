from dotenv import load_dotenv
load_dotenv()
from utils.vector_store import generate_embedding
try:
    print(generate_embedding("Test"))
except Exception as e:
    print("Error:", e)
