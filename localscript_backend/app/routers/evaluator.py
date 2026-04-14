from __future__ import annotations

from fastapi import APIRouter

from app.schemas.evaluation import EvaluateCodeRequest, EvaluateCodeResponse, EvaluationReport
from app.services.code_validation_service import CodeValidationService
from app.services.confidence_service import ConfidenceService
from app.services.evaluation_report_service import EvaluationReportService
from app.services.lua_runtime_validation_service import LuaRuntimeValidationService
from app.services.lua_syntax_service import LuaSyntaxService
from app.services.output_format_service import OutputFormatService
from app.services.scenario_validation_service import ScenarioValidationService
from app.services.task_analysis_service import TaskAnalysisService

router = APIRouter(prefix="/evaluate", tags=["evaluator"])


@router.post("", response_model=EvaluateCodeResponse)
async def evaluate_code(payload: EvaluateCodeRequest) -> EvaluateCodeResponse:
    analysis_service = TaskAnalysisService()
    validation_service = CodeValidationService(
        syntax_service=LuaSyntaxService(),
        runtime_service=LuaRuntimeValidationService(),
    )
    scenario_validation_service = ScenarioValidationService()
    confidence_service = ConfidenceService()
    evaluation_report_service = EvaluationReportService()
    output_format_service = OutputFormatService()

    analysis = analysis_service.analyze(payload.task)

    base_task_contract = {
        "goal": analysis.goal,
        "inputs": analysis.inputs,
        "outputs": analysis.outputs,
        "constraints": analysis.constraints,
        "assumptions": analysis.assumptions,
        "target_runtime": analysis.target_runtime,
        "complexity_note": analysis.complexity_note,
        "task_type": analysis.task_type,
        "task_subtype": analysis.task_subtype,
        "risk_flags": analysis.risk_flags,
        "domain_profile": analysis.domain_profile,
        "profile_rules": analysis.profile_rules,
    }

    output_mode = output_format_service.detect_mode(
        task=payload.task,
        task_contract=base_task_contract,
    )

    task_contract = {
        **base_task_contract,
        "output_mode": output_mode,
    }

    validation = await validation_service.validate(
        code=payload.code,
        task=payload.task,
        validate_runtime=payload.validate_runtime,
    )

    if validation.stage_results.get("policy") and validation.stage_results.get("syntax"):
        scenario_result = scenario_validation_service.validate(
            code=payload.code,
            task=payload.task,
            task_contract=task_contract,
        )
        validation.stage_results["scenario"] = scenario_result.is_valid
        validation.errors.extend(scenario_result.errors)
        validation.warnings.extend(scenario_result.warnings)
        validation.is_valid = len(validation.errors) == 0
    else:
        validation.stage_results["scenario"] = False

    score, reasons = confidence_service.calculate(
        validation=validation,
        repaired=False,
        attempts=1,
        used_history=False,
        task_contract=task_contract,
        selected_templates=[],
        output_mode=output_mode,
    )

    report = evaluation_report_service.build_report(
        context_mode="evaluation_only",
        task_contract=task_contract,
        selected_templates=[],
        output_mode=output_mode,
        validation=validation,
        repaired=False,
        attempts=1,
        confidence_score=score,
        confidence_reasons=reasons,
        provider="manual",
        model="manual-evaluation",
        diff_text=None,
    )

    return EvaluateCodeResponse(
        validation={
            "is_valid": validation.is_valid,
            "stage_results": validation.stage_results,
            "errors": validation.errors,
            "warnings": validation.warnings,
        },
        confidence={
            "score": score,
            "reasons": reasons,
        },
        evaluation_report=EvaluationReport(**report),
    )