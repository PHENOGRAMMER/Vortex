from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.auth.jwt_handler import decode_access_token
from backend.auth.models import User
from backend.db.database import get_db

# HTTPBearer (not OAuth2PasswordBearer) since our /auth/login takes a JSON
# body, not an OAuth2 form. This lets Swagger's "Authorize" dialog accept
# a raw pasted token after you call /auth/login manually.
bearer_scheme = HTTPBearer()

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    email = decode_access_token(credentials.credentials)
    if email is None:
        raise CREDENTIALS_EXCEPTION
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
