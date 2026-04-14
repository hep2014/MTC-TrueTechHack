from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

from app.services.chat_history_service import ChatHistoryService
from app.services.code_extraction_service import CodeExtractionService
from app.services.code_validation_service import CodeValidationService, ValidationResult
from app.services.confidence_service import ConfidenceService
from app.services.diff_service import DiffService
from app.services.evaluation_report_service import EvaluationReportService
from app.services.generation_service import GenerationService
from app.services.local_template_service import LocalTemplateService
from app.services.ollama_chat_client import ChatMessage
from app.services.output_format_service import OutputFormatService
from app.services.pipeline_trace_service import PipelineTraceService
from app.services.prompt_service import PromptService
from app.services.repair_service import RepairService
from app.services.scenario_validation_service import ScenarioValidationService
from app.services.task_analysis_service import TaskAnalysisService


@dataclass
class PipelineResult:
    status: str
    code: str
    output_mode: str
    wrapped_code: str | None
    json_output: str | None
    provider: str
    model: str
    repaired: bool
    attempts: int
    validation: ValidationResult
    used_history: bool
    clarification_questions: list[dict[str, str]]
    task_contract: dict
    confidence_score: int
    confidence_reasons: list[str]
    pipeline_steps: list[dict]
    evaluation_report: dict
    diff_text: str | None


class GenerationOrchestrator:
    def __init__(
        self,
        local_template_service: LocalTemplateService,
        scenario_validation_service: ScenarioValidationService,
        output_format_service: OutputFormatService,
        evaluation_report_service: EvaluationReportService,
        diff_service: DiffService,
        generation_service: GenerationService,
        repair_service: RepairService,
        extraction_service: CodeExtractionService,
        validation_service: CodeValidationService,
        prompt_service: PromptService,
        task_analysis_service: TaskAnalysisService,
        confidence_service: ConfidenceService,
        pipeline_trace_service: PipelineTraceService,
        chat_history_service: ChatHistoryService | None = None,
        max_attempts: int = 2,
    ) -> None:
        self._local_template_service = local_template_service
        self._scenario_validation_service = scenario_validation_service
        self._output_format_service = output_format_service
        self._evaluation_report_service = evaluation_report_service
        self._diff_service = diff_service
        self._generation_service = generation_service
        self._repair_service = repair_service
        self._extraction_service = extraction_service
        self._validation_service = validation_service
        self._prompt_service = prompt_service
        self._task_analysis_service = task_analysis_service
        self._confidence_service = confidence_service
        self._pipeline_trace_service = pipeline_trace_service
        self._chat_history_service = chat_history_service
        self._max_attempts = max_attempts

    async def run(
        self,
        task: str,
        analysis_task: str | None = None,
        history: list[ChatMessage] | None = None,
        session_id: str | None = None,
        validate_runtime: bool = True,
        session_title: str | None = None,
        original_user_message: str | None = None,
        context_mode: str = "new_task",
    ) -> PipelineResult:
        used_history = False
        effective_history: list[ChatMessage] = []
        session = None

        if history:
            effective_history = list(history)
            used_history = True
        elif session_id and self._chat_history_service is not None:
            effective_history = await self._chat_history_service.get_chat_messages(session_id=session_id)
            used_history = len(effective_history) > 0

        if session_id and self._chat_history_service is not None:
            session = await self._chat_history_service.ensure_session(
                session_id=session_id,
                title=session_title,
            )
        elif session_id:
            session = await self._pipeline_trace_service.get_session_by_session_id(session_id)

        previous_assistant_code = self._extract_previous_assistant_code(effective_history)

        run = await self._pipeline_trace_service.start_run(
            session=session,
            user_prompt=analysis_task or task,
            validate_runtime=validate_runtime,
            used_history=used_history,
        )

        started = perf_counter()
        await self._pipeline_trace_service.add_step(
            run=run,
            name="context_resolution",
            status="ok",
            started_at=started,
            details={
                "context_mode": context_mode,
                "used_history": used_history,
            },
        )

        started = perf_counter()
        effective_analysis_task = analysis_task or task
        analysis = self._task_analysis_service.analyze(effective_analysis_task)
        await self._pipeline_trace_service.add_step(
            run=run,
            name="task_analysis",
            status="ok",
            started_at=started,
            details={
                "needs_clarification": analysis.needs_clarification,
                "questions_count": len(analysis.questions),
                "target_runtime": analysis.target_runtime,
                "task_type": analysis.task_type,
                "task_subtype": analysis.task_subtype,
                "domain_profile": analysis.domain_profile,
            },
        )

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

        output_mode = self._output_format_service.detect_mode(
            task=effective_analysis_task,
            task_contract=base_task_contract,
        )

        task_contract = {
            **base_task_contract,
            "output_mode": output_mode,
        }

        started = perf_counter()
        await self._pipeline_trace_service.add_step(
            run=run,
            name="output_mode_selection",
            status="ok",
            started_at=started,
            details={
                "output_mode": output_mode,
            },
        )

        selected_templates = self._local_template_service.select_templates(
            task=effective_analysis_task,
            task_contract=task_contract,
            max_items=2,
        )
        selected_template_keys = [item.key for item in selected_templates]

        started = perf_counter()
        await self._pipeline_trace_service.add_step(
            run=run,
            name="template_selection",
            status="ok",
            started_at=started,
            details={
                "selected_templates": selected_template_keys,
            },
        )

        empty_validation = ValidationResult(
            is_valid=False,
            stage_results={
                "non_empty": False,
                "policy": False,
                "syntax": False,
                "domain": False,
                "runtime": False,
                "scenario": False,
            },
            errors=[],
            warnings=[],
        )

        if analysis.needs_clarification:
            score, reasons = self._confidence_service.calculate_for_clarification(
                questions_count=len(analysis.questions),
                used_history=used_history,
                task_contract=task_contract,
            )

            evaluation_report = self._evaluation_report_service.build_report(
                context_mode=context_mode,
                task_contract=task_contract,
                selected_templates=selected_template_keys,
                output_mode=output_mode,
                validation=empty_validation,
                repaired=False,
                attempts=0,
                confidence_score=score,
                confidence_reasons=reasons,
                provider="",
                model="",
                diff_text=None,
            )

            if session_id and self._chat_history_service is not None:
                await self._chat_history_service.append_message(
                    session_id=session_id,
                    role="user",
                    content=original_user_message or task,
                    title=session_title,
                )

                clarification_text = "\n".join(
                    f"- {item['question']}" for item in analysis.questions
                )

                await self._chat_history_service.append_message(
                    session_id=session_id,
                    role="assistant",
                    content=(
                        "Нужно уточнить несколько моментов перед генерацией Lua-кода:\n"
                        f"{clarification_text}"
                    ),
                    title=session_title,
                )

            await self._pipeline_trace_service.finalize_run(
                run=run,
                status="needs_clarification",
                provider=None,
                model=None,
                repaired=False,
                attempts=0,
                final_code=None,
                confidence_score=score,
                confidence_reasons=reasons,
                task_contract=task_contract,
                clarification_questions=analysis.questions,
            )

            return PipelineResult(
                status="needs_clarification",
                code="",
                output_mode=output_mode,
                wrapped_code=None,
                json_output=None,
                provider="",
                model="",
                repaired=False,
                attempts=0,
                validation=empty_validation,
                used_history=used_history,
                clarification_questions=analysis.questions,
                task_contract=task_contract,
                confidence_score=score,
                confidence_reasons=reasons,
                pipeline_steps=self._pipeline_trace_service.to_list(),
                evaluation_report=evaluation_report,
                diff_text=None,
            )

        if session_id and self._chat_history_service is not None:
            await self._chat_history_service.append_message(
                session_id=session_id,
                role="user",
                content=original_user_message or task,
                title=session_title,
            )

        started = perf_counter()
        generation = await self._generation_service.generate(
            task=task,
            history=effective_history,
            task_contract=task_contract,
        )
        await self._pipeline_trace_service.add_step(
            run=run,
            name="generation",
            status="ok",
            started_at=started,
            details={
                "provider": generation.provider,
                "model": generation.model,
            },
        )

        current_messages = list(generation.messages)
        current_code = self._extraction_service.extract_lua(generation.code)

        started = perf_counter()
        current_validation = await self._validation_service.validate(
            code=current_code,
            task=task,
            validate_runtime=validate_runtime,
        )
        await self._pipeline_trace_service.add_step(
            run=run,
            name="validation_attempt_1",
            status="ok" if current_validation.is_valid else "failed",
            started_at=started,
            details={
                "errors": current_validation.errors,
                "warnings": current_validation.warnings,
                "stage_results": current_validation.stage_results,
            },
        )

        if current_validation.stage_results.get("policy") and current_validation.stage_results.get("syntax"):
            started = perf_counter()
            scenario_result = self._scenario_validation_service.validate(
                code=current_code,
                task=task,
                task_contract=task_contract,
            )
            current_validation.stage_results["scenario"] = scenario_result.is_valid
            current_validation.errors.extend(scenario_result.errors)
            current_validation.warnings.extend(scenario_result.warnings)
            current_validation.is_valid = len(current_validation.errors) == 0

            await self._pipeline_trace_service.add_step(
                run=run,
                name="scenario_validation_attempt_1",
                status="ok" if scenario_result.is_valid else "failed",
                started_at=started,
                details={
                    "errors": scenario_result.errors,
                    "warnings": scenario_result.warnings,
                    "checks": scenario_result.checks,
                },
            )
        else:
            current_validation.stage_results["scenario"] = False

        if current_validation.is_valid:
            formatted = self._output_format_service.format_output(
                code=current_code,
                mode=output_mode,
            )

            diff_text = self._build_diff_if_needed(
                previous_code=previous_assistant_code,
                current_code=formatted.code,
                context_mode=context_mode,
            )

            if diff_text:
                started = perf_counter()
                await self._pipeline_trace_service.add_step(
                    run=run,
                    name="code_diff",
                    status="ok",
                    started_at=started,
                    details={
                        "has_diff": True,
                    },
                )

            started = perf_counter()
            await self._pipeline_trace_service.add_step(
                run=run,
                name="output_formatting",
                status="ok",
                started_at=started,
                details={
                    "output_mode": formatted.mode,
                    "has_wrapped_code": formatted.wrapped_code is not None,
                    "has_json_output": formatted.json_output is not None,
                },
            )

            if session_id and self._chat_history_service is not None:
                assistant_content = formatted.json_output or formatted.wrapped_code or formatted.code
                await self._chat_history_service.append_message(
                    session_id=session_id,
                    role="assistant",
                    content=assistant_content,
                    title=session_title,
                )

            score, reasons = self._confidence_service.calculate(
                validation=current_validation,
                repaired=False,
                attempts=1,
                used_history=used_history,
                task_contract=task_contract,
                selected_templates=selected_template_keys,
                output_mode=output_mode,
            )

            evaluation_report = self._evaluation_report_service.build_report(
                context_mode=context_mode,
                task_contract=task_contract,
                selected_templates=selected_template_keys,
                output_mode=output_mode,
                validation=current_validation,
                repaired=False,
                attempts=1,
                confidence_score=score,
                confidence_reasons=reasons,
                provider=generation.provider,
                model=generation.model,
                diff_text=diff_text,
            )

            status = "completed_with_warnings" if current_validation.warnings else "completed"

            await self._pipeline_trace_service.finalize_run(
                run=run,
                status=status,
                provider=generation.provider,
                model=generation.model,
                repaired=False,
                attempts=1,
                final_code=formatted.code,
                confidence_score=score,
                confidence_reasons=reasons,
                task_contract=task_contract,
                clarification_questions=[],
            )

            return PipelineResult(
                status=status,
                code=formatted.code,
                output_mode=formatted.mode,
                wrapped_code=formatted.wrapped_code,
                json_output=formatted.json_output,
                provider=generation.provider,
                model=generation.model,
                repaired=False,
                attempts=1,
                validation=current_validation,
                used_history=used_history,
                clarification_questions=[],
                task_contract=task_contract,
                confidence_score=score,
                confidence_reasons=reasons,
                pipeline_steps=self._pipeline_trace_service.to_list(),
                evaluation_report=evaluation_report,
                diff_text=diff_text,
            )

        for attempt in range(2, self._max_attempts + 1):
            repair_user_message = self._prompt_service.build_repair_user_message(
                task=task,
                invalid_code=current_code,
                errors=current_validation.errors,
                warnings=current_validation.warnings,
            )

            started = perf_counter()
            repaired = await self._repair_service.repair(
                base_messages=current_messages,
                repair_user_message=repair_user_message,
                invalid_code=current_code,
            )
            await self._pipeline_trace_service.add_step(
                run=run,
                name=f"repair_attempt_{attempt}",
                status="ok",
                started_at=started,
                details={},
            )

            current_messages = list(repaired.messages)
            current_code = self._extraction_service.extract_lua(repaired.code)

            started = perf_counter()
            current_validation = await self._validation_service.validate(
                code=current_code,
                task=task,
                validate_runtime=validate_runtime,
            )
            await self._pipeline_trace_service.add_step(
                run=run,
                name=f"validation_attempt_{attempt}",
                status="ok" if current_validation.is_valid else "failed",
                started_at=started,
                details={
                    "errors": current_validation.errors,
                    "warnings": current_validation.warnings,
                    "stage_results": current_validation.stage_results,
                },
            )

            if current_validation.stage_results.get("policy") and current_validation.stage_results.get("syntax"):
                started = perf_counter()
                scenario_result = self._scenario_validation_service.validate(
                    code=current_code,
                    task=task,
                    task_contract=task_contract,
                )
                current_validation.stage_results["scenario"] = scenario_result.is_valid
                current_validation.errors.extend(scenario_result.errors)
                current_validation.warnings.extend(scenario_result.warnings)
                current_validation.is_valid = len(current_validation.errors) == 0

                await self._pipeline_trace_service.add_step(
                    run=run,
                    name=f"scenario_validation_attempt_{attempt}",
                    status="ok" if scenario_result.is_valid else "failed",
                    started_at=started,
                    details={
                        "errors": scenario_result.errors,
                        "warnings": scenario_result.warnings,
                        "checks": scenario_result.checks,
                    },
                )
            else:
                current_validation.stage_results["scenario"] = False

            if current_validation.is_valid:
                formatted = self._output_format_service.format_output(
                    code=current_code,
                    mode=output_mode,
                )

                diff_text = self._build_diff_if_needed(
                    previous_code=previous_assistant_code,
                    current_code=formatted.code,
                    context_mode=context_mode,
                )

                if diff_text:
                    started = perf_counter()
                    await self._pipeline_trace_service.add_step(
                        run=run,
                        name=f"code_diff_attempt_{attempt}",
                        status="ok",
                        started_at=started,
                        details={
                            "has_diff": True,
                        },
                    )

                started = perf_counter()
                await self._pipeline_trace_service.add_step(
                    run=run,
                    name=f"output_formatting_attempt_{attempt}",
                    status="ok",
                    started_at=started,
                    details={
                        "output_mode": formatted.mode,
                        "has_wrapped_code": formatted.wrapped_code is not None,
                        "has_json_output": formatted.json_output is not None,
                    },
                )

                if session_id and self._chat_history_service is not None:
                    assistant_content = formatted.json_output or formatted.wrapped_code or formatted.code
                    await self._chat_history_service.append_message(
                        session_id=session_id,
                        role="assistant",
                        content=assistant_content,
                        title=session_title,
                    )

                score, reasons = self._confidence_service.calculate(
                    validation=current_validation,
                    repaired=True,
                    attempts=attempt,
                    used_history=True,
                    task_contract=task_contract,
                    selected_templates=selected_template_keys,
                    output_mode=output_mode,
                )

                evaluation_report = self._evaluation_report_service.build_report(
                    context_mode=context_mode,
                    task_contract=task_contract,
                    selected_templates=selected_template_keys,
                    output_mode=output_mode,
                    validation=current_validation,
                    repaired=True,
                    attempts=attempt,
                    confidence_score=score,
                    confidence_reasons=reasons,
                    provider=repaired.provider,
                    model=repaired.model,
                    diff_text=diff_text,
                )

                status = "completed_with_warnings" if current_validation.warnings else "completed"

                await self._pipeline_trace_service.finalize_run(
                    run=run,
                    status=status,
                    provider=repaired.provider,
                    model=repaired.model,
                    repaired=True,
                    attempts=attempt,
                    final_code=formatted.code,
                    confidence_score=score,
                    confidence_reasons=reasons,
                    task_contract=task_contract,
                    clarification_questions=[],
                )

                return PipelineResult(
                    status=status,
                    code=formatted.code,
                    output_mode=formatted.mode,
                    wrapped_code=formatted.wrapped_code,
                    json_output=formatted.json_output,
                    provider=repaired.provider,
                    model=repaired.model,
                    repaired=True,
                    attempts=attempt,
                    validation=current_validation,
                    used_history=True,
                    clarification_questions=[],
                    task_contract=task_contract,
                    confidence_score=score,
                    confidence_reasons=reasons,
                    pipeline_steps=self._pipeline_trace_service.to_list(),
                    evaluation_report=evaluation_report,
                    diff_text=diff_text,
                )

        score, reasons = self._confidence_service.calculate(
            validation=current_validation,
            repaired=True,
            attempts=self._max_attempts,
            used_history=True,
            task_contract=task_contract,
            selected_templates=selected_template_keys,
            output_mode=output_mode,
        )

        evaluation_report = self._evaluation_report_service.build_report(
            context_mode=context_mode,
            task_contract=task_contract,
            selected_templates=selected_template_keys,
            output_mode=output_mode,
            validation=current_validation,
            repaired=True,
            attempts=self._max_attempts,
            confidence_score=score,
            confidence_reasons=reasons,
            provider=generation.provider,
            model=generation.model,
            diff_text=None,
        )

        if session_id and self._chat_history_service is not None:
            failed_text_parts: list[str] = [
                "Не удалось получить полностью валидный результат.",
            ]

            if current_code.strip():
                failed_text_parts.append("Последняя версия Lua-кода:")
                failed_text_parts.append(current_code.strip())

            if current_validation.errors:
                failed_text_parts.append("")
                failed_text_parts.append("Ошибки валидации:")
                failed_text_parts.extend(f"- {item}" for item in current_validation.errors)

            if current_validation.warnings:
                failed_text_parts.append("")
                failed_text_parts.append("Предупреждения:")
                failed_text_parts.extend(f"- {item}" for item in current_validation.warnings)

            await self._chat_history_service.append_message(
                session_id=session_id,
                role="assistant",
                content="\n".join(failed_text_parts).strip(),
                title=session_title,
            )

        await self._pipeline_trace_service.finalize_run(
            run=run,
            status="failed_validation",
            provider=generation.provider,
            model=generation.model,
            repaired=True,
            attempts=self._max_attempts,
            final_code=current_code,
            confidence_score=score,
            confidence_reasons=reasons,
            task_contract=task_contract,
            clarification_questions=[],
        )

        return PipelineResult(
            status="failed_validation",
            code=current_code,
            output_mode=output_mode,
            wrapped_code=None,
            json_output=None,
            provider=generation.provider,
            model=generation.model,
            repaired=True,
            attempts=self._max_attempts,
            validation=current_validation,
            used_history=True,
            clarification_questions=[],
            task_contract=task_contract,
            confidence_score=score,
            confidence_reasons=reasons,
            pipeline_steps=self._pipeline_trace_service.to_list(),
            evaluation_report=evaluation_report,
            diff_text=None,
        )

    def _extract_previous_assistant_code(
        self,
        history: list[ChatMessage],
    ) -> str | None:
        for msg in reversed(history):
            if msg.role == "assistant" and msg.content.strip():
                return msg.content.strip()
        return None

    def _build_diff_if_needed(
        self,
        previous_code: str | None,
        current_code: str,
        context_mode: str,
    ) -> str | None:
        if context_mode not in {"refinement", "clarification"}:
            return None
        if not previous_code:
            return None
        if previous_code.strip() == current_code.strip():
            return None
        return self._diff_service.build_unified_diff(
            old_code=previous_code,
            new_code=current_code,
        )
