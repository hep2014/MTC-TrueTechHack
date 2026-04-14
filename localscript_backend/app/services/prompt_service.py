from __future__ import annotations


class PromptService:
    GENERATION_SYSTEM_PROMPT = """
Ты локальный AI-агент для генерации корректного Lua-кода.

Правила:
- возвращай только чистый Lua-код;
- не используй markdown и fenced code blocks;
- не добавляй объяснений до и после кода;
- код должен быть синтаксически корректным;
- не выдумывай API и глобальные объекты;
- если данных недостаточно, выбери наиболее безопасную и минимальную реализацию;
- предпочитай стандартную библиотеку Lua, если иное не указано явно.
""".strip()

    REPAIR_SYSTEM_PROMPT = """
Ты локальный AI-агент для исправления Lua-кода.

Правила:
- возвращай только исправленный Lua-код;
- не используй markdown;
- исправляй только реальные ошибки валидации;
- сохраняй смысл исходной задачи;
- не добавляй пояснений.
""".strip()

    def build_generation_user_message(
        self,
        task: str,
        task_contract: dict | None = None,
        local_templates: list[dict] | None = None,
    ) -> str:
        contract_block = ""
        profile_block = ""
        template_block = ""

        if task_contract:
            contract_block = (
                "\n\nКонтракт задачи:\n"
                f"- Цель: {task_contract.get('goal', '')}\n"
                f"- Входы: {', '.join(task_contract.get('inputs', [])) or 'не указаны'}\n"
                f"- Выходы: {', '.join(task_contract.get('outputs', [])) or 'не указаны'}\n"
                f"- Ограничения: {', '.join(task_contract.get('constraints', [])) or 'не указаны'}\n"
                f"- Допущения: {', '.join(task_contract.get('assumptions', [])) or 'не указаны'}\n"
                f"- Целевая среда: {task_contract.get('target_runtime', 'lua')}\n"
                f"- Тип задачи: {task_contract.get('task_type', 'unknown')}\n"
                f"- Подтип задачи: {task_contract.get('task_subtype', '')}\n"
                f"- Доменный профиль: {task_contract.get('domain_profile', 'general')}\n"
            )

            profile_rules = task_contract.get("profile_rules", [])
            if profile_rules:
                profile_block = "\nДоменные правила:\n" + "\n".join(
                    f"- {rule}" for rule in profile_rules
                )

        if local_templates:
            chunks: list[str] = []
            for idx, item in enumerate(local_templates, start=1):
                chunks.append(
                    f"Шаблон {idx}: {item['title']}\n"
                    f"Когда применять: {item['when_to_use']}\n"
                    f"Пример Lua:\n{item['lua_example']}"
                )
            template_block = "\n\nЛокальные шаблоны-эталоны:\n" + "\n\n".join(chunks)

        return (
            "Сгенерируй Lua-код для следующей задачи.\n\n"
            f"Задача:\n{task.strip()}"
            f"{contract_block}"
            f"{profile_block}"
            f"{template_block}\n\n"
            "Используй шаблоны как ориентир по стилю и подходу, но адаптируй код под текущую задачу.\n"
            "Верни только чистый Lua-код."
        )

    def build_repair_user_message(
        self,
        task: str,
        invalid_code: str,
        errors: list[str],
        warnings: list[str],
    ) -> str:
        errors_text = "\n".join(f"- {item}" for item in errors) if errors else "- отсутствуют"
        warnings_text = "\n".join(f"- {item}" for item in warnings) if warnings else "- отсутствуют"

        return (
            "Исправь Lua-код после валидации.\n\n"
            f"Исходная задача:\n{task.strip()}\n\n"
            f"Текущий код:\n{invalid_code.strip()}\n\n"
            f"Ошибки:\n{errors_text}\n\n"
            f"Предупреждения:\n{warnings_text}\n\n"
            "Верни только исправленный Lua-код."
        )