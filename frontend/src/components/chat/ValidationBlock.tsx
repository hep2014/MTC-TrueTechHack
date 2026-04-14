import type { ChatGenerateResponse } from "../../types/chat";
import { mapValidation } from "../../utils/validation";

function getStatusText(itemKey: string, ok: boolean): string {
  if (ok) {
    switch (itemKey) {
      case "non_empty":
        return "Результат получен";
      case "policy":
        return "Ограничения соблюдены";
      case "syntax":
        return "Синтаксис корректен";
      case "domain":
        return "Логика уместна";
      case "runtime":
        return "Запуск успешен";
      case "scenario":
        return "Сценарий пройден";
      default:
        return "Проверка пройдена";
    }
  }

  switch (itemKey) {
    case "non_empty":
      return "Ответ пустой";
    case "policy":
      return "Есть запрещённые конструкции";
    case "syntax":
      return "Есть синтаксическая ошибка";
    case "domain":
      return "Есть несоответствие задаче";
    case "runtime":
      return "Во время запуска есть ошибка";
    case "scenario":
      return "Ожидаемый сценарий не подтверждён";
    default:
      return "Проверка не пройдена";
  }
}

export function ValidationBlock({
  meta,
}: {
  meta: ChatGenerateResponse | null;
}) {
  const data = mapValidation(meta);
  if (!data) return null;

  return (
    <div className="validation-block">
      <div className="section-title validation-block__title">
        {data.isValid ? "Проверка пройдена" : "Результат требует внимания"}
      </div>

      <div className="validation-grid validation-grid--detailed">
        {data.items.map((item) => (
          <div
            key={item.key}
            className={`validation-card ${item.ok ? "validation-card--ok" : "validation-card--fail"}`}
          >
            <div className="validation-card__top">
              <div className="validation-card__label">{item.label}</div>
              <div
                className={`validation-card__badge ${
                  item.ok
                    ? "validation-card__badge--ok"
                    : "validation-card__badge--fail"
                }`}
              >
                {item.ok ? "OK" : "Ошибка"}
              </div>
            </div>

            <div className="validation-card__status">
              {getStatusText(item.key, item.ok)}
            </div>

            <div className="validation-card__description">
              {item.description}
            </div>
          </div>
        ))}
      </div>

      {data.errors.length > 0 && (
        <div className="notice notice--error">
          <div className="section-title">Что именно не прошло</div>
          <div className="notice__text">
            {data.errors.join("\n")}
          </div>
        </div>
      )}

      {data.warnings.length > 0 && (
        <div className="notice notice--warn">
          <div className="section-title">На что стоит обратить внимание</div>
          <div className="notice__text">
            {data.warnings.join("\n")}
          </div>
        </div>
      )}
    </div>
  );
}