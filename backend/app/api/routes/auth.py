from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.schemas.auth import SignupRequest, Token, UserOut

router = APIRouter(prefix="/auth")


def normalize_email(email: str) -> str:
    """Emails are case-insensitive in practice, so store and match them lowercased
    to stop Foo@x.com and foo@x.com becoming two separate accounts."""
    return email.strip().lower()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)) -> User:
    email = normalize_email(request.email)
    existing = db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, hashed_password=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = db.scalar(select(User).where(User.email == normalize_email(form_data.username)))
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
