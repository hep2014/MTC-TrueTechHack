from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.generation import GenerateCodeRequest, GenerateCodeResponse, ValidationInfo
from app.schemas.pipeline import ClarificationQuestion, ConfidenceInfo, TaskContract
from app.services.chat_history_service import ChatHistoryService
from app.services.code_extraction_service import CodeExtractionService
from app.services.code_validation_service import CodeValidationService
from app.services.confidence_service import ConfidenceService
from app.services.generation_orchestrator import GenerationOrchestrator
from app.services.generation_service import GenerationService
from app.services.lua_runtime_validation_service import LuaRuntimeValidationService
from app.services.lua_syntax_service import LuaSyntaxService
from app.services.ollama_chat_client import ChatMessage, OllamaChatClient
from app.services.pipeline_trace_service import PipelineTraceService
from app.services.prompt_service import PromptService
from app.services.repair_service import RepairService
from app.services.task_analysis_service import TaskAnalysisService
from app.services.local_template_service import LocalTemplateService
from app.services.diff_service import DiffService
from app.services.evaluation_report_service import EvaluationReportService
from app.services.output_format_service import OutputFormatService
from app.services.scenario_validation_service import ScenarioValidationService


router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("", response_model=GenerateCodeResponse)
async def generate_code(
    payload: GenerateCodeRequest,
    db: AsyncSession = Depends(get_db_session),
) -> GenerateCodeResponse:
    prompt_service = PromptService()
    chat_client = OllamaChatClient()

    generation_service = GenerationService(
        chat_client=chat_client,
        prompt_service=prompt_service,
    )
    repair_service = RepairService(
        chat_client=chat_client,
        prompt_service=prompt_service,
    )
    extraction_service = CodeExtractionService()
    validation_service = CodeValidationService(
        syntax_service=LuaSyntaxService(),
        runtime_service=LuaRuntimeValidationService(),
    )
    chat_history_service = ChatHistoryService(db)
    task_analysis_service = TaskAnalysisService()
    confidence_service = ConfidenceService()
    pipeline_trace_service = PipelineTraceService(db)

    orchestrator = GenerationOrchestrator(
        local_template_service=LocalTemplateService(),
        scenario_validation_service=ScenarioValidationService(),
        output_format_service=OutputFormatService(),
        evaluation_report_service=EvaluationReportService(),
        diff_service=DiffService(),
        generation_service=generation_service,
        repair_service=repair_service,
        extraction_service=extraction_service,
        validation_service=validation_service,
        prompt_service=prompt_service,
        task_analysis_service=task_analysis_service,
        confidence_service=confidence_service,
        pipeline_trace_service=pipeline_trace_service,
        chat_history_service=chat_history_service,
        max_attempts=2,
    )
    history = [
        ChatMessage(role=msg.role, content=msg.content)
        for msg in payload.messages
    ] if payload.messages else None

    result = await orchestrator.run(
        task=payload.prompt,
        history=history,
        session_id=payload.session_id,
        validate_runtime=payload.validate_runtime,
    )

    return GenerateCodeResponse(
        status=result.status,
        code=result.code,
        output_mode=result.output_mode,
        wrapped_code=result.wrapped_code,
        json_output=result.json_output,
        diff_text=result.diff_text,
        provider=result.provider,
        model=result.model,
        repaired=result.repaired,
        attempts=result.attempts,
        used_history=result.used_history,
        validation=ValidationInfo(
            is_valid=result.validation.is_valid,
            stage_results=result.validation.stage_results,
            errors=result.validation.errors,
            warnings=result.validation.warnings,
        ),
        clarification_questions=[
            ClarificationQuestion(**item)
            for item in result.clarification_questions
        ],
        task_contract=TaskContract(**result.task_contract),
        confidence=ConfidenceInfo(
            score=result.confidence_score,
            reasons=result.confidence_reasons,
        ),
        evaluation_report=result.evaluation_report,
        pipeline_steps=result.pipeline_steps,
    )