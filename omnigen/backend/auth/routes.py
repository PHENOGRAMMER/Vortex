from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.auth.dependencies import get_current_user
from backend.auth.jwt_handler import create_access_token, hash_password, verify_password
from backend.auth.models import User
from backend.auth.schemas import TokenOut, UserCreate, UserLogin, UserOut
from backend.db.database import get_db

router = APIRouter()
settings = get_settings()


def create_or_get_oauth_user(db: Session, email: str, provider: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    is_first_user = db.query(User).count() == 0
    user = User(
        email=email,
        hashed_password=hash_password(f"oauth:{provider}:{email}:{settings.jwt_secret}"),
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def redirect_with_token(user: User) -> RedirectResponse:
    token = create_access_token(subject=user.email)
    return RedirectResponse(f"{settings.frontend_url}/chat?token={token}")


def require_oauth_config(provider: str, client_id: str, client_secret: str) -> None:
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=501,
            detail=f"{provider} OAuth is not configured on the backend yet.",
        )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # First user to ever register becomes admin automatically, so there's
    # always at least one admin without manual DB editing on first deploy.
    is_first_user = db.query(User).count() == 0

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_admin=is_first_user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/oauth/google/start")
def google_start():
    require_oauth_config("Google", settings.google_client_id, settings.google_client_secret)
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    return RedirectResponse(f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}")


@router.get("/oauth/google/callback")
async def google_callback(code: str = Query(...), db: Session = Depends(get_db)):
    require_oauth_config("Google", settings.google_client_id, settings.google_client_secret)
    async with httpx.AsyncClient(timeout=20) as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()

    email = user_resp.json().get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google did not return an email address")
    return redirect_with_token(create_or_get_oauth_user(db, email, "google"))


@router.get("/oauth/github/start")
def github_start():
    require_oauth_config("GitHub", settings.github_client_id, settings.github_client_secret)
    params = {
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_redirect_uri,
        "scope": "read:user user:email",
    }
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{urlencode(params)}")


@router.get("/oauth/github/callback")
async def github_callback(code: str = Query(...), db: Session = Depends(get_db)):
    require_oauth_config("GitHub", settings.github_client_id, settings.github_client_secret)
    async with httpx.AsyncClient(timeout=20) as client:
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_redirect_uri,
            },
        )
        token_resp.raise_for_status()
        access_token = token_resp.json().get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="GitHub did not return an access token")
        emails_resp = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        emails_resp.raise_for_status()

    emails = emails_resp.json()
    primary = next((e for e in emails if e.get("primary") and e.get("verified")), None)
    fallback = next((e for e in emails if e.get("verified")), None)
    email = (primary or fallback or {}).get("email")
    if not email:
        raise HTTPException(status_code=400, detail="GitHub did not return a verified email address")
    return redirect_with_token(create_or_get_oauth_user(db, email, "github"))
