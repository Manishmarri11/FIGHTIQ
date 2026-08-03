from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized

    # A validly-signed token could still carry a non-numeric subject; treat that
    # as unauthenticated rather than letting int() raise a 500.
    try:
        user_pk = int(user_id)
    except (TypeError, ValueError):
        raise unauthorized

    user = db.get(User, user_pk)
    if user is None:
        raise unauthorized

    return user


__all__ = ["get_db", "get_current_user"]
