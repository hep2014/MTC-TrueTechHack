from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.chat import router as chat_router
from app.routers.generation import router as generation_router
from app.routers.model import router as model_router
from app.routers.runs import router as runs_router
from app.routers.validation import router as validation_router
from app.routers.chat_generate import router as chat_generate_router
from app.routers.evaluator import router as evaluator_router

app = FastAPI(
    title=settings.app_title,
    debug=settings.app_debug,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(model_router)
app.include_router(validation_router)
app.include_router(generation_router)
app.include_router(chat_router)
app.include_router(runs_router)
app.include_router(chat_generate_router)
app.include_router(evaluator_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}