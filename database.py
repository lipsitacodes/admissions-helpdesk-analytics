import os
from pathlib import Path
from typing import Optional

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "admissions_helpdesk")

_client: Optional[MongoClient] = None


def get_database() -> Database:
    global _client

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is not set. Add your MongoDB Atlas connection string to .env."
        )

    if _client is None:
        _client = MongoClient(
            MONGODB_URI,
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000,
            retryWrites=True,
        )

    _client.admin.command("ping")
    return _client[DATABASE_NAME]