from __future__ import annotations

from dataclasses import dataclass, field
import re

from app.services.domain_profile_service import DomainProfileService


@dataclass
class AnalysisResult:
    needs_clarification: bool
    questions: list[dict[str, str]] = field(default_factory=list)
    goal: str = ""
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    target_runtime: str = "lua"
    complexity_note: str = ""
    task_type: str = "unknown"
    task_subtype: str = ""
    risk_flags: list[str] = field(default_factory=list)
    domain_profile: str = "general"
    profile_rules: list[str] = field(default_factory=list)


class TaskAnalysisService:
    def __init__(self) -> None:
        self._domain_profile_service = DomainProfileService()

    def analyze(self, task: str) -> AnalysisResult:
        text = task.strip()
        lowered = text.lower()

        task_type, task_subtype = self._classify_task(lowered)
        domain_profile = self._domain_profile_service.detect_profile(text)
        profile_rules = self._domain_profile_service.build_profile_rules(domain_profile)

        inputs = self._extract_inputs(text, lowered, task_type, domain_profile)
        outputs = self._extract_outputs(text, lowered, task_type, domain_profile)
        constraints = self._extract_constraints(lowered)
        assumptions: list[str] = []
        questions: list[dict[str, str]] = []
        risk_flags: list[str] = []

        goal = self._extract_goal(text)
        target_runtime = self._detect_runtime(lowered, domain_profile)
        complexity_note = self._detect_complexity_note(lowered)

        has_explicit_function_signature = self._has_function_signature_hint(text)
        has_clear_return_intent = self._has_return_intent(lowered)
        has_clear_print_intent = self._has_print_intent(lowered)
        has_explicit_lowcode_context = self._has_explicit_lowcode_context(lowered)
        lowcode_has_obvious_data_path = self._has_obvious_lowcode_data_path(text)

        looks_like_simple_function_task = (
            task_type == "function_implementation"
            and has_explicit_function_signature
            and (has_clear_return_intent or bool(outputs))
        )

        looks_like_simple_lowcode_task = (
            domain_profile == "lowcode"
            and has_explicit_lowcode_context
            and lowcode_has_obvious_data_path
        )

        if not inputs:
            if looks_like_simple_function_task:
                assumptions.append("Входные данные интерпретируются как аргументы явно указанной функции.")
            elif looks_like_simple_lowcode_task:
                assumptions.append("Входные данные уже доступны по явно указанному LowCode-пути.")
            else:
                questions.append({
                    "key": "input_format",
                    "question": "Какой формат входных данных ожидается: аргументы функции, строка, таблица Lua или чтение из stdin?"
                })
                risk_flags.append("missing_input_format")

        if not outputs:
            if looks_like_simple_function_task:
                assumptions.append("Результат должен возвращаться через return.")
                outputs = ["return value"]
            elif looks_like_simple_lowcode_task:
                assumptions.append("Результат должен возвращаться через return.")
                outputs = ["return value"]
            elif task_type == "script_generation" and has_clear_print_intent:
                outputs = ["stdout"]
            else:
                questions.append({
                    "key": "output_format",
                    "question": "Что должен вернуть или напечатать Lua-код: одно значение, таблицу, строку или побочный эффект?"
                })
                risk_flags.append("missing_output_contract")

        if self._needs_lua_version_question(lowered, task_type, constraints, domain_profile):
            questions.append({
                "key": "lua_version",
                "question": "Для какой версии Lua нужен код: Lua 5.1, Lua 5.3, Lua 5.4 или LuaJIT?"
            })
            if domain_profile == "lowcode":
                assumptions.append(
                    "Для LowCode используется доменный Lua-профиль из контура платформы."
                )
            else:
                assumptions.append(
                    "Если версия Lua не указана, используется максимально совместимый код на стандартной библиотеке Lua."
                )
            risk_flags.append("version_sensitive")

        if self._looks_like_external_api_task(lowered):
            if domain_profile == "lowcode" and has_explicit_lowcode_context:
                assumptions.append(
                    "Разрешённый доменный контекст LowCode определяется по wf.vars, wf.initVariables и _utils.array.*."
                )
            elif not self._has_allowed_api_hint(lowered):
                questions.append({
                    "key": "allowed_apis",
                    "question": "Какие API, глобальные объекты или доменные функции точно разрешено использовать в этом окружении?"
                })
                risk_flags.append("external_api_context")

        questions = self._deduplicate_questions(questions)[:3]
        needs_clarification = self._should_require_clarification(
            task_type=task_type,
            domain_profile=domain_profile,
            questions=questions,
            risk_flags=risk_flags,
            looks_like_simple_function_task=looks_like_simple_function_task,
            looks_like_simple_lowcode_task=looks_like_simple_lowcode_task,
        )

        if not needs_clarification:
            questions = []
            risk_flags = [
                item for item in risk_flags
                if item not in {"missing_input_format", "missing_output_contract", "version_sensitive", "external_api_context"}
            ]

        return AnalysisResult(
            needs_clarification=needs_clarification,
            questions=questions,
            goal=goal,
            inputs=inputs,
            outputs=outputs,
            constraints=constraints,
            assumptions=self._deduplicate(assumptions),
            target_runtime=target_runtime,
            complexity_note=complexity_note,
            task_type=task_type,
            task_subtype=task_subtype,
            risk_flags=self._deduplicate(risk_flags),
            domain_profile=domain_profile,
            profile_rules=profile_rules,
        )

    def _classify_task(self, lowered: str) -> tuple[str, str]:
        if any(token in lowered for token in [
            "lowcode",
            "wf.vars",
            "wf.initvariables",
            "workflow",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
            "_utils.array.new",
            "_utils.array.markasarray",
            "lua{",
            "}lua",
        ]):
            return "lowcode_workflow", "workflow_snippet"

        if self._has_function_signature_hint(lowered) or "функц" in lowered or "function" in lowered:
            if any(token in lowered for token in ["сумм", "sum", "разност", "умнож", "делен", "factorial", "факториал"]):
                return "function_implementation", "numeric_function"
            if any(token in lowered for token in ["строк", "string", "trim", "split", "substring", "паттерн"]):
                return "function_implementation", "string_function"
            if any(token in lowered for token in ["таблиц", "table", "массив", "array", "list"]):
                return "function_implementation", "table_function"
            return "function_implementation", "generic_function"

        if any(token in lowered for token in ["stdin", "print", "скрипт", "script", "stdout"]):
            return "script_generation", "standalone_script"

        if any(token in lowered for token in ["json", "csv", "parse", "парс", "xml"]):
            return "data_transformation", "parsing"

        if any(token in lowered for token in ["сорт", "поиск", "graph", "dfs", "bfs", "dynamic programming", "dp"]):
            return "algorithmic_task", "algorithm"

        return "unknown", ""

    def _extract_goal(self, text: str) -> str:
        compact = " ".join(text.split())
        return compact[:240]

    def _extract_inputs(self, text: str, lowered: str, task_type: str, domain_profile: str) -> list[str]:
        found: list[str] = []

        signature_args = self._extract_function_args(text)
        if signature_args:
            found.append(f"function arguments: {', '.join(signature_args)}")

        if "stdin" in lowered:
            found.append("stdin")
        if "строк" in lowered or "string" in lowered:
            found.append("string")
        if "таблиц" in lowered or "table" in lowered:
            found.append("table")
        if "массив" in lowered or "array" in lowered or "list" in lowered:
            found.append("array-like table")
        if "чис" in lowered or "number" in lowered:
            found.append("number")

        if domain_profile == "lowcode":
            lowcode_paths = self._extract_lowcode_paths(text)
            found.extend(lowcode_paths)

        if task_type == "function_implementation" and signature_args:
            return self._deduplicate(found)

        return self._deduplicate(found)

    def _extract_outputs(self, text: str, lowered: str, task_type: str, domain_profile: str) -> list[str]:
        found: list[str] = []

        if self._has_return_intent(lowered):
            found.append("return value")

        if self._has_print_intent(lowered):
            found.append("stdout")

        if any(token in lowered for token in [
            "одно значение",
            "одно число",
            "single value",
            "single result",
        ]):
            found.append("return value")

        if "таблиц" in lowered and (
                "верни" in lowered or "return" in lowered or "возвращ" in lowered
        ):
            found.append("table")

        if "строк" in lowered and (
                "верни" in lowered or "return" in lowered or "возвращ" in lowered
        ):
            found.append("string")

        if "бул" in lowered or "boolean" in lowered or "true" in lowered or "false" in lowered:
            if "верни" in lowered or "return" in lowered or "возвращ" in lowered:
                found.append("boolean")

        if task_type == "function_implementation" and not found and self._has_function_signature_hint(text):
            found.append("return value")

        if domain_profile == "lowcode" and not found:
            if any(token in lowered for token in [
                "получи",
                "получи последний",
                "верни",
                "увелич",
                "отфильтр",
                "конверт",
                "преобраз",
            ]):
                found.append("return value")

        return self._deduplicate(found)

    def _extract_constraints(self, lowered: str) -> list[str]:
        result: list[str] = []

        if "не использовать" in lowered:
            result.append("Есть явные запреты на часть API.")
        if "без " in lowered:
            result.append("В задаче есть ограничения на допустимые средства реализации.")
        if "только стандарт" in lowered or "standard library only" in lowered:
            result.append("Разрешена только стандартная библиотека Lua.")
        if "lua 5.1" in lowered:
            result.append("Требуется Lua 5.1.")
        if "lua 5.3" in lowered:
            result.append("Требуется Lua 5.3.")
        if "lua 5.4" in lowered:
            result.append("Требуется Lua 5.4.")
        if "luajit" in lowered:
            result.append("Требуется LuaJIT.")
        if "без require" in lowered:
            result.append("Нельзя использовать require.")
        if "без io" in lowered:
            result.append("Нельзя использовать io.")
        if "без os" in lowered:
            result.append("Нельзя использовать os.")
        if "jsonpath" in lowered and ("не используй" in lowered or "не использовать" in lowered):
            result.append("Нельзя использовать JsonPath.")

        return self._deduplicate(result)

    def _detect_runtime(self, lowered: str, domain_profile: str) -> str:
        if "luajit" in lowered:
            return "luajit"
        if "lua 5.1" in lowered:
            return "lua5.1"
        if "lua 5.3" in lowered:
            return "lua5.3"
        if "lua 5.4" in lowered:
            return "lua5.4"
        if domain_profile == "lowcode":
            return "lowcode_lua"
        return "lua"

    def _detect_complexity_note(self, lowered: str) -> str:
        if any(word in lowered for word in ["o(", "сложност", "асимптот", "big-o", "оптим"]):
            return "Задача содержит требования к алгоритмической эффективности."
        return ""

    def _needs_lua_version_question(
        self,
        lowered: str,
        task_type: str,
        constraints: list[str],
        domain_profile: str,
    ) -> bool:
        if any(token in lowered for token in ["lua 5.1", "lua 5.3", "lua 5.4", "luajit"]):
            return False

        if domain_profile == "lowcode":
            return False

        if task_type == "function_implementation":
            return False

        if any("Требуется Lua" in item or "LuaJIT" in item for item in constraints):
            return False

        return True

    def _looks_like_external_api_task(self, lowered: str) -> bool:
        return any(token in lowered for token in [
            "api",
            "http",
            "rest",
            "lowcode",
            "wf.",
            "redis",
            "sql",
            "postgres",
            "mysql",
            "ngx.",
            "kafka",
            "rabbitmq",
            "_utils.",
            "jsonpath",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
        ])

    def _has_allowed_api_hint(self, lowered: str) -> bool:
        return any(token in lowered for token in [
            "можно использовать",
            "разрешено использовать",
            "доступны api",
            "доступны функции",
            "use only",
            "allowed api",
        ])

    def _has_function_signature_hint(self, text: str) -> bool:
        return bool(re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\([^()]*\)", text))

    def _extract_function_args(self, text: str) -> list[str]:
        match = re.search(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(([^()]*)\)", text)
        if not match:
            return []

        raw_args = match.group(1).strip()
        if not raw_args:
            return []

        result: list[str] = []
        for item in raw_args.split(","):
            arg = item.strip()
            if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", arg):
                result.append(arg)

        return result

    def _has_return_intent(self, lowered: str) -> bool:
        return any(token in lowered for token in [
            "верни",
            "вернуть",
            "возвращ",
            "return",
            "должна вернуть",
            "должен вернуть",
        ])

    def _has_print_intent(self, lowered: str) -> bool:
        return any(token in lowered for token in [
            "вывед",
            "напечат",
            "print",
            "stdout",
        ])

    def _has_explicit_lowcode_context(self, lowered: str) -> bool:
        return any(token in lowered for token in [
            "lowcode",
            "wf.vars",
            "wf.initvariables",
            "_utils.array.new",
            "_utils.array.markasarray",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
            "lua{",
            "}lua",
        ])

    def _has_obvious_lowcode_data_path(self, text: str) -> bool:
        return bool(re.search(r"\bwf\.(vars|initVariables)\.[A-Za-z0-9_\.]+", text))

    def _extract_lowcode_paths(self, text: str) -> list[str]:
        matches = re.findall(r"\bwf\.(?:vars|initVariables)\.[A-Za-z0-9_\.]+", text)
        return self._deduplicate(matches)

    def _should_require_clarification(
        self,
        task_type: str,
        domain_profile: str,
        questions: list[dict[str, str]],
        risk_flags: list[str],
        looks_like_simple_function_task: bool,
        looks_like_simple_lowcode_task: bool,
    ) -> bool:
        if looks_like_simple_function_task:
            return False

        if looks_like_simple_lowcode_task:
            return False

        if domain_profile == "lowcode":
            blocking_flags = [flag for flag in risk_flags if flag not in {"version_sensitive", "external_api_context"}]
            return len(blocking_flags) > 0

        if task_type == "function_implementation" and len(questions) <= 1 and "external_api_context" not in risk_flags:
            return False

        if task_type in {"script_generation", "data_transformation", "algorithmic_task", "unknown"} and questions:
            return True

        if "external_api_context" in risk_flags:
            return True

        return len(questions) > 0

    def _deduplicate(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                result.append(value)
        return result

    def _deduplicate_questions(self, values: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        result: list[dict[str, str]] = []
        for item in values:
            key = item["key"]
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result