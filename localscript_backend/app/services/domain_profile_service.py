from __future__ import annotations


class DomainProfileService:
    def detect_profile(self, task: str) -> str:
        lowered = task.lower()

        lowcode_markers = [
            "wf.vars",
            "wf.initvariables",
            "lowcode",
            "_utils.array.new",
            "_utils.array.markasarray",
            "jsonpath",
            "restbody",
            "parsedcsv",
            "idoc",
            "zcdf_",
            "lua{",
            "}lua",
        ]

        if any(marker in lowered for marker in lowcode_markers):
            return "lowcode"

        return "general"

    def build_profile_rules(self, profile: str) -> list[str]:
        if profile == "lowcode":
            return [
                "Используй прямой доступ к данным через wf.vars и wf.initVariables.",
                "Не используй JsonPath.",
                "Если задача про массивы в LowCode, допускается _utils.array.new() и _utils.array.markAsArray(arr).",
                "Если пользователь явно просит встраиваемый формат, допускается подготовка кода для lua{...}lua, но базовый ответ должен оставаться чистым Lua.",
                "Не выдумывай недокументированные объекты, кроме wf.vars, wf.initVariables и _utils.array.* в соответствующем контексте.",
            ]

        return [
            "Используй стандартный Lua без доменно-специфичных API, если они явно не указаны в задаче."
        ]