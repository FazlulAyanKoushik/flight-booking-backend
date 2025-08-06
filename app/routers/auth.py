from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import async_session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserRead, Token
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/register", response_model=UserRead)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = await auth_service.hash_password(user.password)
    db_user = User(email=user.email, password=hashed_password, role=user.role)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if not db_user or not await auth_service.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = await auth_service.create_access_token({"sub": str(db_user.id), "role": db_user.role})
    return {"access_token": access_token, "token_type": "bearer"}
