from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db, settings
from app.models import User
from app.schemas import UserCreate, UserLogin, User as UserSchema, Token
from app.utils.auth import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    get_current_active_user
)

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя
    """
    # Проверка существования пользователя
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с такой электронной почтой уже зарегистрирован"
        )
    
    # Создание нового пользователя
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    del user_data["password"]
    
    db_user = User(
        **user_data,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Авторизация пользователя (получение JWT токена)
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная электронная почта или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=Token)
def login_json(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Авторизация пользователя через JSON (альтернатива form-data)
    """
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная электронная почта или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Аккаунт деактивирован",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Получить информацию о текущем пользователе
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о текущем пользователе
    """
    # Запрещенные для обновления поля
    forbidden_fields = {"id", "email", "hashed_password", "is_active", "is_verified", "created_at", "updated_at"}
    
    # Фильтруем обновляемые поля
    allowed_updates = {k: v for k, v in user_update.items() if k not in forbidden_fields and v is not None}
    
    if not allowed_updates:
        raise HTTPException(status_code=400, detail="Нет полей для обновления")
    
    # Обновляем пользователя
    for field, value in allowed_updates.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/profile", response_model=UserSchema)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Получить профиль пользователя (алиас для /me)
    """
    return current_user