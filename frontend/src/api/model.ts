import { apiFetch } from "./client";
import type { ModelCheckResponse } from "../types/tools";

export function checkModel(prompt = "ping"): Promise<ModelCheckResponse> {
  return apiFetch<ModelCheckResponse>("/model/check", {
    method: "POST",
    body: JSON.stringify({ prompt }),
  });
}