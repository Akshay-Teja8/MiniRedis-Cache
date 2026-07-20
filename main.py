"""
FastAPI service exposing the thread-safe LRU+TTL cache over HTTP.

Run with:
    uvicorn app.main:app --reload
"""

from typing import Any, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from lru_cache import LRUcache

app = FastAPI(title="MiniRedis Cache API", version="0.1.0")

# One shared cache instance for the process. In a real deployment you'd
# likely back this with Redis for multi-instance consistency -- see
# README "Scaling beyond a single process".
cache = LRUcache(capacity=1000, sweep_interval=5.0)


class PutRequest(BaseModel):
    value: Any
    ttl: Optional[float] = None  # seconds; omit for no expiry


class PutResponse(BaseModel):
    key: str
    stored: bool


class GetResponse(BaseModel):
    key: str
    value: Any
    found: bool

@app.get("/", tags=["System"])
def root():
    return {
        "service": "MiniRedis Cache API",
        "version": "1.0.0",
        "documentation": "/docs",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": " MiniRedis Cache API",
        "version": "1.0.0"
    }


@app.get("/stats")
def stats():
    return {
    "cache": cache.get_stats()
}

@app.get("/cache/{key}", response_model=GetResponse)
def get_key(key: str):
    value = cache.get(key)
    if value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"key '{key}' not found or expired")
    return GetResponse(key=key, value=value, found=True)


@app.put("/cache/{key}", response_model=PutResponse)
def put_key(key: str, body: PutRequest):
    cache.put(key, body.value, ttl=body.ttl)
    return PutResponse(key=key, stored=True)


@app.delete("/cache/{key}")
def delete_key(key: str):
    deleted = cache.delete(key)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"key '{key}' not found")
    return {"key": key, "deleted": True}

@app.delete("/cache")
def clear_cache():
    cache.clear()
    return {"cleared": True,"current_size": len(cache), "capacity": cache.capacity}

@app.on_event("shutdown")
def shutdown_event():
    cache.stop_sweeper()


