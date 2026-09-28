import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "Clinica-RAG")

client = MongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where()
)
db = client[DB_NAME]

users_collection = db["users"]
reports_collection = db["reports"]
diagnosis_collection = db["diagnosis_history"]