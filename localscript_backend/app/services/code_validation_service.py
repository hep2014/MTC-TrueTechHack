from __future__ import annotations

from dataclasses import dataclass, field
import re

from app.services.lua_runtime_validation_service import LuaRuntimeValidationService
from app.services.lua_syntax_service import LuaSyntaxService


@dataclass
class ValidationResult:
    is_valid: bool
    stage_results: dict[str, bool] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class CodeValidationService:
    def __init__(
        self,
        syntax_service: LuaSyntaxService,
        runtime_service: LuaRuntimeValidationService,
    ) -> None:
        self._syntax_service = syntax_service
        self._runtime_service = runtime_service

        self._forbidden_patterns: list[tuple[str, str]] = [
            (r"```", "Код не должен содержать markdown-блоки."),
            (r"(?i)jsonpath", "Запрещено использовать JsonPath."),
            (r"\bos\.execute\s*\(", "Запрещено использовать os.execute."),
            (r"\bio\.popen\s*\(", "Запрещено использовать io.popen."),
            (r"\brequire\s*\(", "Запрещено использовать require."),
            (r"\bdebug\.", "Запрещено использовать debug API."),
            (r"\bloadstring\s*\(", "Запрещено использовать loadstring."),
            (r"\bdofile\s*\(", "Запрещено использовать dofile."),
            (r"\bpackage\.", "Запрещено использовать package API."),
        ]

        self._suspicious_patterns: list[tuple[str, str]] = [
            (r"\bhttp[s]?:\/\/", "В коде замечены URL-адреса, это может быть признаком галлюцинации."),
            (r"\bconsole\.log\b", "Найден console.log, что не относится к Lua."),
            (r"\bSystem\.", "Найден System.*, что не относится к Lua."),
            (r"\bundefined\b", "Найден undefined, что не относится к Lua."),
            (r"\bimport\s+", "Найдена конструкция import, что не относится к Lua."),
        ]

        self._non_lua_markers: list[str] = [
            "function main(",
            "public static",
            "console.log",
            "System.out",
            "def ",
            "const ",
            "let ",
            "var ",
            "=>",
        ]

    async def validate(
        self,
        code: str,
        task: str = "",
        validate_runtime: bool = True,
    ) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        stage_results: dict[str, bool] = {}

        normalized = code.strip()

        if not normalized:
            return ValidationResult(
                is_valid=False,
                stage_results={
                    "non_empty": False,
                    "policy": False,
                    "syntax": False,
                    "domain": False,
                    "runtime": False,
                },
                errors=["Модель вернула пустой код."],
                warnings=[],
            )

        stage_results["non_empty"] = True

        policy_ok = self._validate_policy(
            code=normalized,
            errors=errors,
            warnings=warnings,
        )
        stage_results["policy"] = policy_ok

        syntax_ok = False
        if policy_ok:
            syntax_ok, syntax_error = await self._syntax_service.validate(normalized)
            if not syntax_ok:
                errors.append(
                    f"Синтаксическая ошибка Lua (luac -p): {syntax_error or 'неизвестная ошибка'}"
                )
        else:
            warnings.append("Синтаксическая проверка luac пропущена из-за policy-ошибок.")
        stage_results["syntax"] = syntax_ok

        domain_ok = self._validate_domain_rules(
            code=normalized,
            task=task,
            errors=errors,
            warnings=warnings,
        )
        stage_results["domain"] = domain_ok

        runtime_ok = False
        runtime_skipped_for_domain = self._should_skip_runtime_for_domain(
            code=normalized,
            task=task,
        )

        if validate_runtime and policy_ok and syntax_ok and not runtime_skipped_for_domain:
            runtime_ok, runtime_error = await self._runtime_service.validate(normalized)
            if not runtime_ok:
                errors.append(
                    f"Ошибка выполнения Lua (lua): {runtime_error or 'неизвестная ошибка'}"
                )
        else:
            if runtime_skipped_for_domain:
                runtime_ok = True
                warnings.append(
                    "Runtime-валидация пропущена: код использует LowCode-глобалы wf/_utils и должен исполняться в доменном контуре."
                )
            elif not validate_runtime:
                warnings.append("Runtime-валидация Lua отключена.")
            elif not policy_ok:
                warnings.append("Runtime-валидация Lua пропущена из-за policy-ошибок.")
            elif not syntax_ok:
                warnings.append("Runtime-валидация Lua пропущена из-за синтаксической ошибки.")
        stage_results["runtime"] = runtime_ok

        return ValidationResult(
            is_valid=len(errors) == 0,
            stage_results=stage_results,
            errors=errors,
            warnings=warnings,
        )

    def _validate_policy(
        self,
        code: str,
        errors: list[str],
        warnings: list[str],
    ) -> bool:
        ok = True

        for pattern, message in self._forbidden_patterns:
            if re.search(pattern, code, flags=re.MULTILINE):
                ok = False
                errors.append(message)

        for pattern, message in self._suspicious_patterns:
            if re.search(pattern, code, flags=re.MULTILINE):
                warnings.append(message)

        for marker in self._non_lua_markers:
            if marker in code:
                ok = False
                errors.append(f"В ответе обнаружена конструкция не из Lua: {marker}")

        return ok

    def _validate_domain_rules(
        self,
        code: str,
        task: str,
        errors: list[str],
        warnings: list[str],
    ) -> bool:
        ok = True
        lowered_task = task.lower()
        lowered_code = code.lower()

        is_lowcode_task = any(token in lowered_task for token in [
            "lowcode",
            "wf.vars",
            "wf.initvariables",
            "_utils.array.new",
            "_utils.array.markasarray",
            "jsonpath",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
            "lua{",
            "}lua",
        ])

        if is_lowcode_task:
            if "jsonpath" in lowered_code:
                ok = False
                errors.append("Для LowCode-задачи нельзя использовать JsonPath.")

            if "wf.vars" not in code and "wf.initVariables" not in code:
                warnings.append(
                    "Для LowCode-задачи в коде не обнаружены wf.vars или wf.initVariables."
                )

            if "lua{" in lowered_code or "}lua" in lowered_code:
                warnings.append(
                    "Похоже, модель вернула LowCode-обёртку lua{...}lua вместо чистого Lua-кода."
                )

            if "_utils.array.new" in code or "_utils.array.markAsArray" in code:
                warnings.append(
                    "Обнаружено использование LowCode array helper API."
                )

        if "верни" in lowered_task or "return" in lowered_task:
            if "return" not in lowered_code:
                warnings.append(
                    "В коде не найден return, хотя задача похожа на выражение с возвратом значения."
                )

        if len(code.strip()) < 3:
            ok = False
            errors.append("Слишком короткий ответ модели: это не похоже на корректный Lua-код.")

        return ok

    def _should_skip_runtime_for_domain(
        self,
        code: str,
        task: str,
    ) -> bool:
        lowered_task = task.lower()

        is_lowcode_task = any(token in lowered_task for token in [
            "lowcode",
            "wf.vars",
            "wf.initvariables",
            "_utils.array.new",
            "_utils.array.markasarray",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
        ])

        uses_lowcode_globals = (
            "wf." in code
            or "_utils." in code
        )

        return is_lowcode_task and uses_lowcode_globals