from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LocalTemplate:
    key: str
    title: str
    tags: list[str]
    when_to_use: str
    lua_example: str


class LocalTemplateService:
    def __init__(self) -> None:
        self._templates = [
            LocalTemplate(
                key="lowcode_last_array_item",
                title="Последний элемент массива в LowCode",
                tags=["lowcode", "wf.vars", "array", "last_item", "email"],
                when_to_use="Когда нужно получить последний элемент массива из wf.vars.",
                lua_example="return wf.vars.emails[#wf.vars.emails]",
            ),
            LocalTemplate(
                key="lowcode_increment_counter",
                title="Инкремент счётчика",
                tags=["lowcode", "wf.vars", "counter", "increment"],
                when_to_use="Когда нужно увеличить числовую переменную на 1.",
                lua_example="return wf.vars.try_count_n + 1",
            ),
            LocalTemplate(
                key="lowcode_filter_array",
                title="Фильтрация массива через _utils.array.new",
                tags=["lowcode", "array", "filter", "_utils.array.new", "parsedcsv"],
                when_to_use="Когда нужно отфильтровать элементы массива и вернуть новый массив в LowCode.",
                lua_example=(
                    "local result = _utils.array.new()\n"
                    "local items = wf.vars.parsedCsv\n"
                    "for _, item in ipairs(items) do\n"
                    "    if (item.Discount ~= \"\" and item.Discount ~= nil) "
                    "or (item.Markdown ~= \"\" and item.Markdown ~= nil) then\n"
                    "        table.insert(result, item)\n"
                    "    end\n"
                    "end\n"
                    "return result"
                ),
            ),
            LocalTemplate(
                key="lowcode_ensure_array",
                title="Нормализация items к массиву",
                tags=["lowcode", "array", "items", "ensure_array", "zcdf_packages"],
                when_to_use="Когда нужно гарантировать, что items представлены массивом.",
                lua_example=(
                    "function ensureArray(t)\n"
                    "    if type(t) ~= \"table\" then\n"
                    "        return {t}\n"
                    "    end\n"
                    "    local isArray = true\n"
                    "    for k, _ in pairs(t) do\n"
                    "        if type(k) ~= \"number\" or math.floor(k) ~= k then\n"
                    "            isArray = false\n"
                    "            break\n"
                    "        end\n"
                    "    end\n"
                    "    return isArray and t or {t}\n"
                    "end\n"
                    "\n"
                    "function ensureAllItemsAreArrays(objectsArray)\n"
                    "    if type(objectsArray) ~= \"table\" then\n"
                    "        return objectsArray\n"
                    "    end\n"
                    "    for _, obj in ipairs(objectsArray) do\n"
                    "        if type(obj) == \"table\" and obj.items then\n"
                    "            obj.items = ensureArray(obj.items)\n"
                    "        end\n"
                    "    end\n"
                    "    return objectsArray\n"
                    "end\n"
                    "\n"
                    "return ensureAllItemsAreArrays(wf.vars.json.IDOC.ZCDF_HEAD.ZCDF_PACKAGES)"
                ),
            ),
            LocalTemplate(
                key="lowcode_iso8601_from_datum_time",
                title="Сборка ISO 8601 из DATUM и TIME",
                tags=["lowcode", "time", "iso8601", "datum", "idoc"],
                when_to_use="Когда нужно преобразовать DATUM/TIME в ISO 8601.",
                lua_example=(
                    "DATUM = wf.vars.json.IDOC.ZCDF_HEAD.DATUM\n"
                    "TIME = wf.vars.json.IDOC.ZCDF_HEAD.TIME\n"
                    "local function safe_sub(str, start_pos, end_pos)\n"
                    "    local s = string.sub(str, start_pos, math.min(end_pos, #str))\n"
                    "    return s ~= \"\" and s or \"00\"\n"
                    "end\n"
                    "year = safe_sub(DATUM, 1, 4)\n"
                    "month = safe_sub(DATUM, 5, 6)\n"
                    "day = safe_sub(DATUM, 7, 8)\n"
                    "hour = safe_sub(TIME, 1, 2)\n"
                    "minute = safe_sub(TIME, 3, 4)\n"
                    "second = safe_sub(TIME, 5, 6)\n"
                    "iso_date = string.format('%s-%s-%sT%s:%s:%s.00000Z', year, month, day, hour, minute, second)\n"
                    "return iso_date"
                ),
            ),
            LocalTemplate(
                key="general_numeric_function",
                title="Чистая Lua-функция с проверкой аргументов",
                tags=["general", "function", "number", "validation"],
                when_to_use="Когда нужно сгенерировать обычную Lua-функцию для чисел.",
                lua_example=(
                    "function sum(a, b)\n"
                    "    if type(a) ~= \"number\" or type(b) ~= \"number\" then\n"
                    "        error(\"Both arguments must be numbers\")\n"
                    "    end\n"
                    "    return a + b\n"
                    "end"
                ),
            ),
        ]

    def select_templates(
        self,
        task: str,
        task_contract: dict,
        max_items: int = 2,
    ) -> list[LocalTemplate]:
        lowered_task = task.lower()
        domain_profile = task_contract.get("domain_profile", "general")
        task_type = task_contract.get("task_type", "unknown")
        subtype = task_contract.get("task_subtype", "")

        scored: list[tuple[int, LocalTemplate]] = []

        for template in self._templates:
            score = 0

            if domain_profile in template.tags:
                score += 5

            if task_type == "lowcode_workflow" and "lowcode" in template.tags:
                score += 4

            if task_type == "function_implementation" and "function" in template.tags:
                score += 3

            if subtype == "numeric_function" and "number" in template.tags:
                score += 2

            token_hits = sum(
                1 for tag in template.tags
                if tag.lower() in lowered_task
            )
            score += token_hits * 2

            if "послед" in lowered_task and "last_item" in template.tags:
                score += 4
            if "увелич" in lowered_task and "increment" in template.tags:
                score += 4
            if "фильтр" in lowered_task and "filter" in template.tags:
                score += 4
            if "iso" in lowered_task and "iso8601" in template.tags:
                score += 4
            if "datum" in lowered_task and "datum" in template.tags:
                score += 4
            if "time" in lowered_task and "time" in template.tags:
                score += 2
            if "items" in lowered_task and "items" in template.tags:
                score += 4
            if "zcdf" in lowered_task and "zcdf_packages" in template.tags:
                score += 4

            if score > 0:
                scored.append((score, template))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [template for _, template in scored[:max_items]]