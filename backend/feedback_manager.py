from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def insert_feedback(question, answer, feedback_type):
    now = datetime.utcnow().isoformat()
    supabase.table("feedback_reports").insert({
        "question": question,
        "answer": answer,
        "feedback_type": feedback_type,
        "reported_at": now
    }).execute()

def list_feedback():
    res = supabase.table("feedback_reports").select("*").order("reported_at", desc=True).execute()
    return res.data if res.data else []
