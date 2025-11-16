from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

from database import db, create_document, get_documents
from schemas import Client, ChecklistItem

app = FastAPI(title="Onboardly API", version="1.0.0")

# CORS for local dev and the hosted preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateClientRequest(Client):
    pass


class CreateChecklistItemRequest(ChecklistItem):
    pass


@app.get("/test")
async def test() -> Dict[str, str]:
    # Also ping the db connection to ensure it's alive
    _ = db
    return {"status": "ok"}


@app.post("/clients", response_model=Dict[str, Any])
async def create_client(payload: CreateClientRequest):
    data = payload.dict()
    inserted = await create_document("client", data)
    return {"id": str(inserted["_id"]), **{k: v for k, v in inserted.items() if k != "_id"}}


@app.get("/clients", response_model=List[Dict[str, Any]])
async def list_clients(status: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    filter_dict: Dict[str, Any] = {}
    if status:
        filter_dict["status"] = status
    if q:
        # simple case-insensitive search on name or company
        filter_dict["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"company": {"$regex": q, "$options": "i"}},
        ]
    docs = await get_documents("client", filter_dict, limit)
    # Normalize id
    result: List[Dict[str, Any]] = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        result.append(d)
    return result


@app.post("/checklist", response_model=Dict[str, Any])
async def create_checklist_item(payload: CreateChecklistItemRequest):
    data = payload.dict()
    inserted = await create_document("checklistitem", data)
    return {"id": str(inserted["_id"]), **{k: v for k, v in inserted.items() if k != "_id"}}


@app.get("/checklist", response_model=List[Dict[str, Any]])
async def list_checklist_items(client_id: Optional[str] = None, limit: int = 100):
    filter_dict: Dict[str, Any] = {}
    if client_id:
        filter_dict["client_id"] = client_id
    docs = await get_documents("checklistitem", filter_dict, limit)
    result: List[Dict[str, Any]] = []
    for d in docs:
        d["id"] = str(d.pop("_id"))
        result.append(d)
    return result
