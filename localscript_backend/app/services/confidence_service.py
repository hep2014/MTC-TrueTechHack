from __future__ import annotations

from app.services.code_validation_service import ValidationResult


class ConfidenceService:
    def calculate(
        self,
        validation: ValidationResult,
        repaired: bool,
        attempts: int,
        used_history: bool,
        task_contract: dict | None = None,
        selected_templates: list[str] | None = None,
        output_mode: str = "pure_lua",
    ) -> tuple[int, list[str]]:
        score = 40
        reasons: list[str] = []

        task_contract = task_contract or {}
        selected_templates = selected_templates or []

        domain_profile = task_contract.get("domain_profile", "general")
        scenario_enabled = "scenario" in validation.stage_results

        if validation.stage_results.get("policy"):
            score += 10
            reasons.append("Код прошёл policy-проверки.")
        else:
            score -= 15
            reasons.append("Есть нарушения policy-проверок.")

        if validation.stage_results.get("syntax"):
            score += 15
            reasons.append("Код прошёл синтаксическую проверку Lua.")
        else:
            score -= 25
            reasons.append("Синтаксическая проверка Lua не пройдена.")

        if validation.stage_results.get("runtime"):
            score += 10
            reasons.append("Код прошёл runtime-валидацию.")
        else:
            score -= 8
            reasons.append("Runtime-валидация не пройдена или не выполнялась.")

        if validation.stage_results.get("domain"):
            score += 6
            reasons.append("Код прошёл доменные эвристики.")
        else:
            score -= 8
            reasons.append("Есть проблемы на уровне доменных эвристик.")

        if scenario_enabled:
            if validation.stage_results.get("scenario"):
                score += 6
                reasons.append("Код прошёл сценарную проверку для класса задачи.")
            else:
                score -= 10
                reasons.append("Код не прошёл сценарную проверку для класса задачи.")

        if domain_profile == "lowcode":
            score += 2
            reasons.append("Активирован доменный профиль LowCode.")

        if selected_templates:
            score += min(3, 2 * len(selected_templates))
            reasons.append("При генерации использованы локальные шаблоны-эталоны.")

        if output_mode != "pure_lua":
            score += 2
            reasons.append("Формат ответа адаптирован под прикладной сценарий использования.")

        if repaired:
            score -= 5
            reasons.append("Понадобилась итерация исправления.")
        else:
            score += 5
            reasons.append("Код прошёл без repair-итерации.")

        if attempts > 1:
            score -= min(6, attempts - 1)
            reasons.append("Понадобились дополнительные попытки генерации/исправления.")

        if validation.warnings:
            penalty = min(len(validation.warnings) * 2, 12)
            score -= penalty
            reasons.append("Есть предупреждения валидации.")

        if validation.errors:
            penalty = min(30, 12 + len(validation.errors) * 4)
            score -= penalty
            reasons.append("Есть ошибки валидации.")

        if used_history:
            score += 2
            reasons.append("При генерации использовалась история диалога.")

        score = max(0, min(100, score))
        return score, reasons

    def calculate_for_clarification(
        self,
        questions_count: int,
        used_history: bool,
        task_contract: dict | None = None,
    ) -> tuple[int, list[str]]:
        score = 38
        reasons: list[str] = [
            "Генерация остановлена до написания кода, потому что в постановке не хватает данных.",
        ]

        task_contract = task_contract or {}
        domain_profile = task_contract.get("domain_profile", "general")
        risk_flags = task_contract.get("risk_flags", [])

        if questions_count == 1:
            score += 12
            reasons.append("Не хватает только одного уточнения.")
        elif questions_count == 2:
            score += 6
            reasons.append("Требуется небольшое число уточнений.")
        else:
            score -= 4
            reasons.append("Постановка задачи пока слишком общая.")

        if domain_profile == "lowcode":
            score += 6
            reasons.append("Система распознала доменный LowCode-контекст.")

        if risk_flags:
            if len(risk_flags) == 1:
                score += 4
                reasons.append("Неопределённость локализована в одном аспекте задачи.")
            elif len(risk_flags) >= 3:
                score -= 4
                reasons.append("Есть несколько недостающих частей постановки.")

        if used_history:
            score += 4
            reasons.append("При анализе была доступна история диалога.")

        score = max(10, min(65, score))
        return score, reasons