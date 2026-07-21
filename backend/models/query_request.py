from pydantic import BaseModel


class QueryRequest(BaseModel):

    query: str

    top_k: int = 5

    document_ids: list[str] | None = None

    filenames: list[str] | None = None
