from fastapi import FastAPI
from app.routers import health, auth
import subprocess
from sqlalchemy.future import select
from app.db import async_session, initialize_db
from app.models.user import User
from app.schemas.user import RoleEnum
from app.services import auth as auth_service

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Run alembic upgrade head
    subprocess.run(["alembic", "upgrade", "head"])
    
    # Initialize database connection
    await initialize_db()

    # Ensure at least one admin user exists
    async with async_session() as session:
        result = await session.execute(select(User).where(User.role == RoleEnum.admin))
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            # Create default admin user
            default_email = "admin@example.com"
            default_password = "admin123"
            hashed_password = await auth_service.hash_password(default_password)
            user = User(email=default_email, password=hashed_password, role=RoleEnum.admin)
            session.add(user)
            await session.commit()
            print(f"Default admin created: {default_email} / {default_password}")
        else:
            print("Admin user already exists.")

app.include_router(health.router)
app.include_router(auth.router)