from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.chat_generate import ChatGenerateRequest, ChatGenerateResponse
from app.schemas.generation import ValidationInfo
from app.schemas.pipeline import ClarificationQuestion, ConfidenceInfo, TaskContract
from app.services.chat_context_service import ChatContextService
from app.services.chat_history_service import ChatHistoryService
from app.services.code_extraction_service import CodeExtractionService
from app.services.code_validation_service import CodeValidationService
from app.services.confidence_service import ConfidenceService
from app.services.generation_orchestrator import GenerationOrchestrator
from app.services.generation_service import GenerationService
from app.services.lua_runtime_validation_service import LuaRuntimeValidationService
from app.services.lua_syntax_service import LuaSyntaxService
from app.services.ollama_chat_client import OllamaChatClient
from app.services.pipeline_trace_service import PipelineTraceService
from app.services.prompt_service import PromptService
from app.services.repair_service import RepairService
from app.services.task_analysis_service import TaskAnalysisService
from app.services.local_template_service import LocalTemplateService
from app.services.diff_service import DiffService
from app.services.evaluation_report_service import EvaluationReportService
from app.services.output_format_service import OutputFormatService
from app.services.scenario_validation_service import ScenarioValidationService

router = APIRouter(prefix="/chat", tags=["chat-generate"])


@router.post("/message", response_model=ChatGenerateResponse)
async def chat_message(
    payload: ChatGenerateRequest,
    db: AsyncSession = Depends(get_db_session),
) -> ChatGenerateResponse:
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
    chat_context_service = ChatContextService(db)
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

    context = await chat_context_service.resolve_context(
        session_id=payload.session_id,
        user_message=payload.message,
    )

    previous_final_code = await chat_context_service.get_previous_final_code(
        session_id=payload.session_id,
    )


    result = await orchestrator.run(
        task=context["effective_task"],
        analysis_task=context["analysis_task"],
        history=None,
        session_id=payload.session_id,
        validate_runtime=payload.validate_runtime,
        session_title=payload.title,
        original_user_message=payload.message,
        context_mode=context["mode"],
        previous_final_code=previous_final_code,
    )

    return ChatGenerateResponse(
        session_id=payload.session_id,
        resumed_from_clarification=context["resumed_from_clarification"],
        resumed_from_refinement=context["resumed_from_refinement"],
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