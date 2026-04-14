from __future__ import annotations

from app.services.code_validation_service import ValidationResult


class EvaluationReportService:
    def build_report(
        self,
        *,
        context_mode: str,
        task_contract: dict,
        selected_templates: list[str],
        output_mode: str,
        validation: ValidationResult,
        repaired: bool,
        attempts: int,
        confidence_score: int,
        confidence_reasons: list[str],
        provider: str,
        model: str,
        diff_text: str | None = None,
    ) -> dict:
        return {
            "context_mode": context_mode,
            "domain_profile": task_contract.get("domain_profile", "general"),
            "task_type": task_contract.get("task_type", "unknown"),
            "task_subtype": task_contract.get("task_subtype", ""),
            "selected_templates": selected_templates,
            "output_mode": output_mode,
            "validation_summary": {
                "is_valid": validation.is_valid,
                "stage_results": dict(validation.stage_results),
                "errors_count": len(validation.errors),
                "warnings_count": len(validation.warnings),
            },
            "repair_used": repaired,
            "attempts": attempts,
            "confidence_score": confidence_score,
            "confidence_reasons": confidence_reasons,
            "provider": provider,
            "model": model,
            "has_diff": bool(diff_text),
            "diff_text": diff_text,
            "final_status": (
                "completed"
                if validation.is_valid and not validation.warnings
                else "completed_with_warnings"
                if validation.is_valid
                else "failed_validation"
            ),
        }