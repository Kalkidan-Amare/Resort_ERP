from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import uvicorn
import os
import sys

from app.core.config import settings
from app.router.routers import router
from app.core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Optional: Add project root to Python path

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }

if __name__ == "__main__":
    # Drop all tables with CASCADE
    # with engine.connect() as connection:
    #     # Disable foreign key checks temporarily
    #     connection.execute(text("DROP SCHEMA public CASCADE;"))
    #     connection.execute(text("CREATE SCHEMA public;"))
    #     connection.execute(text('GRANT ALL ON SCHEMA public TO postgres;'))
    #     connection.execute(text('GRANT ALL ON SCHEMA public TO public;'))
    #     connection.commit()
   

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True) 
