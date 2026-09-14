"""
Revenue OS backend — FastAPI + SQLAlchemy + SQLite.

Run locally:
    uvicorn app.main:app --reload

Interactive API docs then live at http://127.0.0.1:8000/docs
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import leads, messages, insights, dashboard, funnel
from .seed import seed

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Revenue OS API",
    description="Backend for the Revenue OS real-estate sales & marketing dashboard.",
    version="1.0.0",
)

# Allow the deployed frontend (and local dev servers) to call this API.
# Tighten this list to your real frontend origin(s) before going to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://real-estate-ares-258f.vercel.app",
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(leads.router)
app.include_router(messages.router)
app.include_router(insights.router)
app.include_router(funnel.router)


@app.on_event("startup")
def on_startup():
    # Seed with sample data matching the frontend's demo content, but only
    # if the DB is empty — safe to leave in for local/dev use.
    seed()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# Serve the frontend (static/index.html + any assets) from the same app.
# Mounted last so it never shadows the /api/* routes above, and html=True
# means "/" resolves to static/index.html automatically.
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")
