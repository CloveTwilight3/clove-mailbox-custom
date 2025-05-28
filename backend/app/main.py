from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import create_tables
from app.api.v1 import auth, emails, accounts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    yield
    
    # Shutdown
    pass


app = FastAPI(
    title="Personal Email Client API",
    description="A powerful email client backend supporting IMAP, POP3, and SMTP",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include API routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(emails.router, prefix="/api/v1/emails", tags=["emails"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])


@app.get("/")
async def root():
    return {
        "message": "Personal Email Client API", 
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Email client API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
