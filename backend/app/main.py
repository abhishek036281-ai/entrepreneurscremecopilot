from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine
from app.models import base
from app.routes import auth, profile, schemes, admin
from app.seed import seed_verified_data
import os

# Create database tables & seed initial data
base.Base.metadata.create_all(bind=engine)
try:
    if settings.ENVIRONMENT.lower() != "production":
        seed_verified_data()
except Exception as e:
    print(f"Seed note: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()] if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(schemes.router)
app.include_router(admin.router)

# Health check route
@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Entrepreneur Scheme Copilot API is fully operational"}

frontend_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../frontend"
    )
)

if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Entrepreneur Scheme Copilot API is running"
    }
