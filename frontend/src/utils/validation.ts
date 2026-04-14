import type { ChatGenerateResponse } from "../types/chat";

export type UiValidationItem = {
  key: string;
  label: string;
  description: string;
  ok: boolean;
};

const VALIDATION_META: Record<string, { label: string; description: string }> = {
  non_empty: {
    label: "Ответ не пустой",
    description: "Модель действительно вернула содержательный результат, а не пустую строку.",
  },
  policy: {
    label: "Соответствует правилам безопасности",
    description: "В коде не обнаружены запрещённые конструкции и опасные API.",
  },
  syntax: {
    label: "Синтаксис Lua корректный",
    description: "Код проходит синтаксическую проверку и может быть разобран интерпретатором Lua.",
  },
  domain: {
    label: "Соответствует условиям задачи",
    description: "Код выглядит уместным для постановки задачи и не противоречит доменным ограничениям.",
  },
  runtime: {
    label: "Исполняется без ошибок",
    description: "Код проходит runtime-проверку и не падает при запуске в тестовой обёртке.",
  },
  scenario: {
    label: "Проходит сценарную проверку",
    description: "Решение похоже на ожидаемый шаблон для данного класса задач.",
  },
};

export function mapValidation(meta: ChatGenerateResponse | null): {
  isValid: boolean;
  items: UiValidationItem[];
  errors: string[];
  warnings: string[];
} | null {
  if (!meta?.validation) return null;

  const { validation } = meta;

  const items: UiValidationItem[] = Object.entries(
    validation.stage_results || {},
  ).map(([key, value]) => ({
    key,
    label: VALIDATION_META[key]?.label ?? key,
    description:
      VALIDATION_META[key]?.description ??
      "Системная проверка этого этапа выполнена без дополнительного описания.",
    ok: Boolean(value),
  }));

  return {
    isValid: validation.is_valid,
    items,
    errors: validation.errors || [],
    warnings: validation.warnings || [],
  };
}