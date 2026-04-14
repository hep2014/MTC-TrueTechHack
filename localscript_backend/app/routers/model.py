from fastapi import APIRouter, HTTPException, status

from app.schemas.common import ErrorResponse
from app.schemas.model import ModelCheckRequest, ModelCheckResponse
from app.services.ollama_chat_client import OllamaChatClient

router = APIRouter(prefix="/model", tags=["model"])


@router.post(
    "/check",
    response_model=ModelCheckResponse,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def check_model(payload: ModelCheckRequest) -> ModelCheckResponse:
    client = OllamaChatClient()

    try:
        result = await client.ping(payload.prompt)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обращения к модели: {exc}",
        ) from exc

    preview = result.text[:300] if result.text else ""

    return ModelCheckResponse(
        ok=bool(result.text.strip() or result.provider == "stub"),
        provider=result.provider,
        model=result.model,
        preview=preview,
    )