from pydantic import BaseModel, Field


class OpenAIMessage(BaseModel):

    role: str

    content: str


class ChatCompletionRequest(BaseModel):

    model: str = Field(default="auto")

    messages: list[OpenAIMessage]

    temperature: float = 0.7

    max_tokens: int | None = None

    stream: bool = False

    user: str | None = None


class OpenAIChoice(BaseModel):

    index: int

    message: OpenAIMessage

    finish_reason: str = "stop"


class OpenAIUsage(BaseModel):

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int


class ChatCompletionResponse(BaseModel):

    id: str

    object: str = "chat.completion"

    created: int

    model: str

    choices: list[OpenAIChoice]

    usage: OpenAIUsage