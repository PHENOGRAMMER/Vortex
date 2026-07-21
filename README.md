---
title: OmniGen
emoji: "✨"
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# OmniGen

OmniGen is a document-grounded chat application with per-chat document uploads and RAG citations.

## Hugging Face Spaces (free CPU demo)

This repository includes a Docker Space configuration. The free CPU deployment supports chat and document RAG using a cloud API key. Image generation remains available in the local desktop deployment with ComfyUI; it is deliberately disabled in the free hosted demo because it needs a GPU or paid inference credits.

Set these **Space Secrets** before starting the app:

- `GROQ_API_KEY` (recommended) and/or `GEMINI_API_KEY`
- `JWT_SECRET` (use a long random value)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_REDIRECT_URI` if Google login is enabled

Set these **Space Variables**:

```text
ENVIRONMENT=production
FRONTEND_URL=https://YOUR-SPACE-NAME.hf.space
GOOGLE_REDIRECT_URI=https://YOUR-SPACE-NAME.hf.space/auth/oauth/google/callback
CORS_ORIGINS=["https://YOUR-SPACE-NAME.hf.space"]
DATABASE_URL=sqlite:////data/omnigen.db
DATA_DIR=/data
EMBEDDING_PROVIDER=sentence-transformers
DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
ENABLE_LOCAL_IMAGE_GENERATION=false
ENABLE_REMOTE_IMAGE_GENERATION=false
```

The free Space filesystem is ephemeral. Users can use uploads while the Space stays awake, but database records and uploaded documents can disappear after a restart. Use persistent storage or an external database/object store before treating it as a production service.
