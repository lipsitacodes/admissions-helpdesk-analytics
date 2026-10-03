import os
from pathlib import Path
from typing import Optional

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Check both backend/.env and repo root .env
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
if (REPO_ROOT / ".env").exists():
    load_dotenv(REPO_ROOT / ".env")


def get_mongodb_uri() -> str:
    return (os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "").strip()


def get_database_name() -> str:
    return (
        os.getenv("MONGODB_DATABASE")
        or os.getenv("MONGO_DATABASE")
        or "admissions_helpdesk"
    ).strip()


_client: Optional[MongoClient] = None


def get_database() -> Database:
    """Return the connected MongoDB Database instance. Raises RuntimeError if URI not set or unreachable."""
    global _client

    uri = get_mongodb_uri()
    if not uri:
        raise RuntimeError(
            "MongoDB URI is not set. Add MONGODB_URI or MONGO_URI to your .env file."
        )

    db_name = get_database_name()

    if _client is None:
        try:
            _client = MongoClient(
                uri,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True,
            )
            # Test connectivity
            _client.admin.command("ping")
        except Exception:
            # Fallback attempt if explicit certifi is not required by connection string
            _client = MongoClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                retryWrites=True,
            )
            _client.admin.command("ping")

    return _client[db_name]


def check_connection() -> bool:
    """Safely check if MongoDB Atlas is currently reachable without raising an exception."""
    try:
        db = get_database()
        db.command("ping")
        return True
    except Exception:
        return False