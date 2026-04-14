import { apiFetch } from "./client";
import type { EvaluateCodeResponse, ValidateCodeResponse } from "../types/tools";

export function validateLuaCode(payload: {
  code: string;
  task?: string;
  validate_runtime?: boolean;
}): Promise<ValidateCodeResponse> {
  return apiFetch<ValidateCodeResponse>("/validate", {
    method: "POST",
    body: JSON.stringify({
      code: payload.code,
      task: payload.task ?? "",
      validate_runtime: payload.validate_runtime ?? true,
    }),
  });
}

export function evaluateLuaCode(payload: {
  code: string;
  task: string;
  validate_runtime?: boolean;
}): Promise<EvaluateCodeResponse> {
  return apiFetch<EvaluateCodeResponse>("/evaluate", {
    method: "POST",
    body: JSON.stringify({
      code: payload.code,
      task: payload.task,
      validate_runtime: payload.validate_runtime ?? true,
    }),
  });
}