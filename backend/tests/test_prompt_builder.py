from backend.services.prompt_builder import PromptBuilder
from backend.services.text_chunker import TextChunk


chunks = [

    TextChunk(
        index=0,
        text="Aryan knows Python, FastAPI and LangChain.",
        start=0,
        end=45,
    ),

    TextChunk(
        index=1,
        text="He has experience with Machine Learning and RAG.",
        start=46,
        end=100,
    ),
]

prompt = PromptBuilder.build(

    question="What programming languages does Aryan know?",

    chunks=chunks,

)

print(prompt)