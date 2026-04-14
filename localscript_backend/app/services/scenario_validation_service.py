from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScenarioValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)


class ScenarioValidationService:
    def validate(
        self,
        code: str,
        task: str,
        task_contract: dict,
    ) -> ScenarioValidationResult:
        lowered_code = code.lower()
        lowered_task = task.lower()

        domain_profile = task_contract.get("domain_profile", "general")
        task_type = task_contract.get("task_type", "unknown")
        task_subtype = task_contract.get("task_subtype", "")
        inputs = " ".join(task_contract.get("inputs", []))
        outputs = " ".join(task_contract.get("outputs", []))

        errors: list[str] = []
        warnings: list[str] = []
        checks: dict[str, bool] = {}

        checks["non_trivial_code"] = len(code.strip()) >= 8
        if not checks["non_trivial_code"]:
            errors.append("Scenario validation: код слишком короткий для полезного решения.")

        has_return = "return" in lowered_code
        checks["has_return_if_expected"] = True
        if "return value" in outputs and not has_return:
            checks["has_return_if_expected"] = False
            warnings.append("Scenario validation: ожидался return, но он не найден.")

        if domain_profile == "lowcode":
            checks["lowcode_access_pattern"] = ("wf.vars" in code) or ("wf.initVariables" in code)
            if not checks["lowcode_access_pattern"]:
                warnings.append(
                    "Scenario validation: для LowCode-задачи не найден доступ через wf.vars или wf.initVariables."
                )

            checks["no_jsonpath"] = "jsonpath" not in lowered_code
            if not checks["no_jsonpath"]:
                errors.append("Scenario validation: обнаружен JsonPath в LowCode-коде.")



        if task_type == "function_implementation":
            checks["has_function"] = "function" in lowered_code
            if not checks["has_function"]:
                warnings.append("Scenario validation: ожидалась функция, но keyword function не найден.")



        if task_subtype == "numeric_function":
            checks["numeric_pattern"] = any(
                token in lowered_code for token in ["+", "-", "*", "/", "tonumber", "math."]
            )
            if not checks["numeric_pattern"]:
                warnings.append("Scenario validation: для numeric_function не найден числовой паттерн.")



        if ("послед" in lowered_task or "last" in lowered_task) and ("emails" in lowered_task or "array" in lowered_task):
            checks["last_item_pattern"] = "#" in code or "[#" in code
            if not checks["last_item_pattern"]:
                warnings.append("Scenario validation: для задачи про последний элемент массива не найден шаблон доступа по длине массива.")


        if "discount" in lowered_task or "markdown" in lowered_task or "отфильтр" in lowered_task:
            checks["filter_pattern"] = ("for " in lowered_code or "ipairs" in lowered_code) and ("table.insert" in lowered_code or "_utils.array.new" in code)
            if not checks["filter_pattern"]:
                warnings.append("Scenario validation: для задачи фильтрации не найден ожидаемый паттерн цикла и сборки результата.")


        if "items" in lowered_task and ("array" in lowered_task or "массив" in lowered_task):
            checks["ensure_array_pattern"] = "type(" in lowered_code and "table" in lowered_code
            if not checks["ensure_array_pattern"]:
                warnings.append("Scenario validation: для нормализации items к массиву не найден ожидаемый type/table паттерн.")

        if "iso" in lowered_task or "datum" in lowered_task or "time" in lowered_task:
            checks["time_pattern"] = any(
                token in lowered_code for token in ["string.format", "match(", "sub(", "safe_sub", "os.time", "epoch"]
            )
            if not checks["time_pattern"]:
                warnings.append("Scenario validation: для задачи со временем не найден ожидаемый паттерн обработки даты/времени.")

        is_valid = len(errors) == 0
        return ScenarioValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            checks=checks,
        )