"""
routers/auth.py — Authentication endpoints
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.auth_service import AuthService
from backend.schemas.user import UserCreate, UserResponse, Token
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login with username + password, returns JWT token."""
    from backend.database import check_db_connection
    user = AuthService.authenticate(db, form_data.username, form_data.password)
    token = AuthService.create_token(user)
    role = user.role.value if hasattr(user.role, "value") else user.role
    db_status = check_db_connection()
    return Token(
        access_token=token, 
        role=role, 
        username=user.username, 
        user_id=user.id,
        db_connected=db_status
    )


@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (should be admin-protected in production)."""
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=data.username,
        full_name=data.full_name,
        hashed_password=AuthService.hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
