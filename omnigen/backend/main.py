from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from backend.config import get_settings
from backend.router.task_router import route, classify_task
from backend.router.model_clients.base import ModelUnavailableError
from backend.db.database import init_db, get_db
from backend.auth.routes import router as auth_router
from backend.auth.dependencies import get_current_user
from backend.auth.models import User
from backend.chat.models import ChatMessage, ChatSession
from backend.admin.routes import router as admin_router
from backend.admin.logger import log_request
from backend.routes import chat
from backend.core.sse import sse_event
from backend.services.stream_service import fake_stream
from backend import providers
from backend.routes.chat import router as chat_router
from backend.api.providers import router as providers_router
from backend.auth.routes import router as auth_router
from backend.api import providers
from backend.routes.router import router as router_stats_router
from backend.router.rag_router import router as rag_router
from backend.routes.openai import router as openai_router

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["FAISS_NUM_THREADS"] = "1"


router = APIRouter()


@router.post("/stream")
async def stream_chat():

    async def event_generator():
        async for event in fake_stream():
            yield sse_event(event)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

MAX_HISTORY_MESSAGES = 8
MAX_HISTORY_CHARS = 3000
MAX_TOTAL_HISTORY_CHARS = 12000

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["Chat"],
)

app.include_router(
    providers_router,
)

app.include_router(
    rag_router,
)

app.include_router(
    router_stats_router,
)

app.include_router(
    openai_router,
    prefix="/v1",
    tags=["OpenAI Compatible"]
)

class GenerateRequest(BaseModel):
    prompt: str
    session_id: int | None = None
    history: list[dict] = []
    has_context_docs: bool = False  # set True once RAG ingestion is wired in
    image_model: str | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    tokens_used: int
    token_limit: int
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role: str
    content: str
    task_type: str | None = None
    provider: str | None = None
    model: str | None = None


class SessionDetailOut(SessionOut):
    messages: list[MessageOut]


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def get_or_create_session(db: Session, user: User, session_id: int | None, prompt: str) -> ChatSession:
    if session_id:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user.id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return session

    title = prompt[:48].strip() or "New chat"
    session = ChatSession(
        user_id=user.id,
        title=title,
        token_limit=settings.session_token_limit,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def token_payload(session: ChatSession, added_tokens: int = 0) -> dict:
    used = session.tokens_used + added_tokens
    warning = None
    if used >= session.token_limit:
        warning = "This chat session has reached its token limit. Start a new chat to continue."
    elif used >= int(session.token_limit * 0.8):
        warning = "This chat session is close to its token limit."

    return {
        "used": used,
        "limit": session.token_limit,
        "remaining": max(0, session.token_limit - used),
        "warning": warning,
    }


def store_message(
    db: Session,
    session: ChatSession,
    *,
    role: str,
    content: str,
    tokens: int,
    task_type: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> None:
    stored_content = content
    if task_type == "image" and role == "assistant":
        stored_content = "[Generated image omitted from saved session history.]"

    db.add(
        ChatMessage(
            session_id=session.id,
            role=role,
            content=stored_content,
            task_type=task_type,
            provider=provider,
            model=model,
            tokens=tokens,
        )
    )
    session.tokens_used += tokens
    session.updated_at = datetime.now(timezone.utc)
    db.commit()


def safe_history(history: list[dict]) -> list[dict]:
    cleaned: list[dict] = []
    total_chars = 0
    for item in history[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue

        content = str(item.get("content") or "")
        if content.startswith("data:image") or len(content) > 8000:
            content = "[Large previous message omitted from history.]"
        elif len(content) > MAX_HISTORY_CHARS:
            content = f"{content[:MAX_HISTORY_CHARS]}\n[Previous message truncated.]"

        total_chars += len(content)
        if total_chars > MAX_TOTAL_HISTORY_CHARS:
            break
        cleaned.append({"role": role, "content": content})
    return cleaned


def system_prompt_for(task_type):
    if task_type.value == "code":
        return (
            "You are OmniGen, a senior full-stack engineer. When producing code:\n"
            "- Write complete, runnable code with no placeholders, TODOs, or omitted "
            "logic -- every function or handler you reference must actually be "
            "implemented, not stubbed.\n"
            "- Use current, non-deprecated APIs. For React 18+, always use "
            "`createRoot` from `react-dom/client` -- never `ReactDOM.render`. Prefer "
            "hooks over legacy class lifecycle methods unless the user asks otherwise.\n"
            "- If the user asks for interactive behavior (drag-and-drop, click-to-"
            "select, game logic, form validation, etc.), wire up the real event "
            "handlers and state updates that make it work -- do not render a static "
            "UI that merely looks interactive.\n"
            "- Before presenting the code, mentally trace through the main user "
            "interaction once (e.g. 'what happens on the first click') and confirm "
            "the state updates actually produce the intended result.\n"
            "- Default stack for frontend UI requests is React + Vite + Tailwind CSS "
            "unless the user specifies another stack.\n"
            "- Include file names as headers and concise setup/run steps. Keep prose "
            "short; let the code carry the explanation."
        )

    return (
        "You are OmniGen, a precise and helpful AI assistant. Give complete, "
        "well-structured answers with practical next steps. Be concise when the user "
        "asks simple questions, but do not omit important details."
    )


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/sessions", response_model=list[SessionOut])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .limit(50)
        .all()
    )


@app.post("/api/sessions", response_model=SessionOut)
def create_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ChatSession(
        user_id=current_user.id,
        title="New chat",
        token_limit=settings.session_token_limit,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@app.get("/api/sessions/{session_id}", response_model=SessionDetailOut)
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return SessionDetailOut(
        id=session.id,
        title=session.title,
        tokens_used=session.tokens_used,
        token_limit=session.token_limit,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=messages,
    )


@app.post("/api/generate")
async def generate(
    req: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task_type = classify_task(req.prompt, req.has_context_docs)
    session = get_or_create_session(db, current_user, req.session_id, req.prompt)
    request_tokens = estimate_tokens(req.prompt) + sum(
        estimate_tokens(item["content"]) for item in safe_history(req.history)
    )
    if session.tokens_used >= session.token_limit:
        raise HTTPException(status_code=429, detail=token_payload(session))
    if session.tokens_used + request_tokens >= session.token_limit:
        raise HTTPException(status_code=429, detail=token_payload(session, request_tokens))

    messages = [
        {
            "role": "system",
            "content": system_prompt_for(task_type),
        },
        *safe_history(req.history),
        {"role": "user", "content": req.prompt},
    ]
    try:
        task_type, response = await route(
            req.prompt,
            messages,
            req.has_context_docs,
            image_model=req.image_model,
        )
    except ModelUnavailableError as e:
        log_request(
            db,
            user_id=current_user.id,
            task_type=task_type.value,
            status="error",
            error_detail=str(e),
            prompt=req.prompt,
        )
        raise HTTPException(status_code=503, detail=str(e))

    response_tokens = 1000 if task_type.value == "image" else estimate_tokens(str(response.content))
    store_message(
        db,
        session,
        role="user",
        content=req.prompt,
        tokens=estimate_tokens(req.prompt),
        task_type=task_type.value,
    )
    store_message(
        db,
        session,
        role="assistant",
        content=str(response.content),
        tokens=response_tokens,
        task_type=task_type.value,
        provider=response.provider,
        model=response.model,
    )
    db.refresh(session)

    log_request(
        db,
        user_id=current_user.id,
        task_type=task_type.value,
        status="success",
        provider=response.provider,
        model=response.model,
        latency_ms=response.latency_ms,
        prompt=req.prompt,
    )

    return {
        "session_id": session.id,
        "task_type": task_type,
        "provider": response.provider,
        "model": response.model,
        "latency_ms": round(response.latency_ms, 1),
        "content": response.content,
        "token_usage": token_payload(session),
    }
