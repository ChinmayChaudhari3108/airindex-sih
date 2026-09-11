import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine, SessionLocal
from app.routers import scrape, fares, index, forecast


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Auto create database tables on startup
    Base.metadata.create_all(bind=engine)

    # 2. Auto-seed database with realistic AI generated fare quotes if empty
    db = SessionLocal()
    try:
        from app.models import FareObservation
        from app.scraper.runner import run_scrape
        count = db.query(FareObservation).count()
        if count == 0:
            print("[INFO] Database empty — auto-seeding AI synthetic fare observations...")
            await run_scrape(db)
            print("[INFO] Auto-seeding complete! Ingested fare observations into database.")
    except Exception as e:
        print(f"[WARNING] Auto-seeding skipped/error: {e}")
    finally:
        db.close()

    yield


app = FastAPI(
    title="AIRINDEX API",
    description="Real-time airfare price intelligence backend — SIH26056 (Team CyberCrypt).",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(scrape.router)
app.include_router(fares.router)
app.include_router(index.router)
app.include_router(forecast.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "airindex-api"}


# Mount Merged Frontend (served directly from FastAPI at root '/')
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "title": "AIRINDEX API",
            "status": "online",
            "version": "0.1.0",
            "docs": "/docs",
            "health": "/api/v1/health",
            "note": "Frontend dist build not found. Build frontend with 'npm run build' inside frontend/ to serve static UI here."
        }
