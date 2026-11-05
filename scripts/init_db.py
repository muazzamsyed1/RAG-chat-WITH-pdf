"""
Initialize the database and create all tables.
Run this once before starting the backend for the first time.

Usage:
    cd d:/RagPDF1
    python scripts/init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database.base import create_all_tables
from app.config.settings import get_settings


async def main():
    settings = get_settings()
    print(f"Initializing database at: {settings.DATABASE_URL}")
    await create_all_tables()
    print("[SUCCESS] Database tables created successfully!")
    print("\nYou can now start the backend:")
    print("  cd backend")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
