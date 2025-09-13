from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from .core.config import settings
from .core.database import engine, Base
from .api.blocks import router as blocks_router


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Info Central API",
    description="AI-powered dashboard builder backend",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blocks_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Info Central API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)