from fastapi import APIRouter

from app.schemas.validation import ValidateCodeRequest, ValidateCodeResponse
from app.services.code_validation_service import CodeValidationService
from app.services.lua_runtime_validation_service import LuaRuntimeValidationService
from app.services.lua_syntax_service import LuaSyntaxService

router = APIRouter(prefix="/validate", tags=["validation"])


@router.post("", response_model=ValidateCodeResponse)
async def validate_code(payload: ValidateCodeRequest) -> ValidateCodeResponse:
    validation_service = CodeValidationService(
        syntax_service=LuaSyntaxService(),
        runtime_service=LuaRuntimeValidationService(),
    )

    result = await validation_service.validate(
        code=payload.code,
        task=payload.task,
        validate_runtime=payload.validate_runtime,
    )

    return ValidateCodeResponse(
        is_valid=result.is_valid,
        stage_results=result.stage_results,
        errors=result.errors,
        warnings=result.warnings,
    )