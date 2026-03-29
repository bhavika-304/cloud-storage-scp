from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx, os, re, json, tempfile, asyncio, time, hashlib
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import fitz
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ─── INIT ─────────────────────────────────────────
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CONFIG ───────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGO_URL = os.getenv("MONGO_URL")
GROQ_MODEL = "llama-3.1-8b-instant"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ─── MONGO ────────────────────────────────────────
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["research_assistant"]

# ─── RATE LIMIT FIX ───────────────────────────────
_last_request = 0
MIN_DELAY = 3

async def fetch_ss(query):
    global _last_request

    gap = time.time() - _last_request
    if gap < MIN_DELAY:
        await asyncio.sleep(MIN_DELAY - gap)

    _last_request = time.time()

    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params={
            "query": query,
            "limit": 10,
            "fields": "title,abstract,authors,year,externalIds,openAccessPdf,url"
        })

        if r.status_code == 429:
            await asyncio.sleep(5)
            raise HTTPException(429, "Rate limited — wait few seconds")

        return r.json()

# ─── PAPERS ───────────────────────────────────────
@app.get("/papers")
async def get_papers(q: str):
    query = q.lower().strip()

    # 🔥 CACHE FIRST
    cached = await db.papers.find({"query": query}).to_list(10)
    if cached:
        return {"papers": cached, "cached": True}

    data = await fetch_ss(query)

    papers = []
    for p in data.get("data", []):
        ext = p.get("externalIds") or {}
        arxiv = ext.get("ArXiv")

        pdf = (p.get("openAccessPdf") or {}).get("url") or \
              (f"https://arxiv.org/pdf/{arxiv}.pdf" if arxiv else None)

        paper = {
            "paperId": p.get("paperId"),
            "title": p.get("title"),
            "abstract": (p.get("abstract") or "")[:500],
            "authors": [a["name"] for a in p.get("authors", [])[:3]],
            "year": p.get("year"),
            "url": p.get("url"),
            "pdfUrl": pdf,
            "query": query,
            "savedAt": datetime.utcnow()
        }

        papers.append(paper)

        await db.papers.update_one(
            {"paperId": paper["paperId"]},
            {"$set": paper},
            upsert=True
        )

    return {"papers": papers, "cached": False}

# ─── SUMMARIZE ────────────────────────────────────
class SummarizeRequest(BaseModel):
    text: str

@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    if not groq_client:
        raise HTTPException(500, "Missing GROQ API key")

    prompt = f"Summarize this research paper simply:\n{req.text[:4000]}"

    res = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return {"summary": res.choices[0].message.content}

# ─── HEALTH ───────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "model": GROQ_MODEL}