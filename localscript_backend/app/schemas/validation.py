from pydantic import BaseModel, Field


class ValidateCodeRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=1,
        description="Lua-код для проверки",
    )
    task: str = Field(
        default="",
        description="Необязательный исходный текст задачи для доменной валидации",
    )
    validate_runtime: bool = Field(
        default=True,
        description="Нужно ли выполнять runtime-валидацию через lua",
    )


class ValidateCodeResponse(BaseModel):
    is_valid: bool = Field(..., description="Прошла ли валидация")
    stage_results: dict[str, bool] = Field(
        default_factory=dict,
        description="Результаты отдельных этапов валидации",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Ошибки валидации",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Предупреждения валидации",
    )