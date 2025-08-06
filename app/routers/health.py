from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
import os
import sqlite3
import psycopg2

router = APIRouter()

@router.get("/health/db", tags=["health"])
def health_check_db():
    db_type = os.getenv("DATABASE_TYPE", "sqlite3")
    try:
        if db_type == "sqlite3":
            db_path = os.getenv("SQLITE_DB_PATH", "./app.db")
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1;")
            conn.close()
        elif db_type == "postgres":
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", 5432),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", ""),
                dbname=os.getenv("POSTGRES_DB", "postgres")
            )
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.close()
            conn.close()
        else:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"status": "unsupported db type"})
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"status": "unhealthy", "detail": str(e)})
