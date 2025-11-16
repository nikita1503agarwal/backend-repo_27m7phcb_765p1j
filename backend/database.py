import os
from datetime import datetime
from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_db")

_client = AsyncIOMotorClient(DATABASE_URL)
db: AsyncIOMotorDatabase = _client[DATABASE_NAME]


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow()
    data = {**data, "created_at": data.get("created_at") or now, "updated_at": now}
    result = await db[collection_name].insert_one(data)
    inserted = await db[collection_name].find_one({"_id": result.inserted_id})
    return inserted  # contains _id


async def get_documents(collection_name: str, filter_dict: Dict[str, Any] | None = None, limit: int = 50) -> List[Dict[str, Any]]:
    filter_dict = filter_dict or {}
    cursor = db[collection_name].find(filter_dict).sort("created_at", -1).limit(int(limit))
    docs: List[Dict[str, Any]] = []
    async for doc in cursor:
        docs.append(doc)
    return docs
