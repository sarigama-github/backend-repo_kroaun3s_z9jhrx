from typing import Any, Dict, List, Optional
from datetime import datetime
import os
from pymongo import MongoClient
from starlette.concurrency import run_in_threadpool

DATABASE_URL = os.environ.get("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "appdb")

_client: Optional[MongoClient] = None
_db = None

def _get_sync_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(DATABASE_URL, serverSelectionTimeoutMS=5000)
        # Trigger server selection on startup (non-fatal if unavailable)
        try:
            _client.admin.command("ping")
        except Exception:
            # In this environment the DB might not be reachable; operations will still try later
            pass
    return _client

def _get_sync_db():
    global _db
    if _db is None:
        client = _get_sync_client()
        _db = client[DATABASE_NAME]
    return _db

async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    db = _get_sync_db()
    now = datetime.utcnow()
    data["created_at"] = now
    data["updated_at"] = now

    def _insert():
        result = db[collection_name].insert_one(data)
        data["id"] = str(result.inserted_id)
        data["_id"] = result.inserted_id
        return data

    return await run_in_threadpool(_insert)

async def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    db = _get_sync_db()

    def _find():
        docs: List[Dict[str, Any]] = []
        for doc in db[collection_name].find(filter_dict or {}).limit(limit):
            doc["id"] = str(doc.get("_id"))
            docs.append(doc)
        return docs

    return await run_in_threadpool(_find)
