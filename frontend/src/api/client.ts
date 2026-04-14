const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const rawText = await response.text();

  if (!response.ok) {
    throw new Error(rawText || `HTTP ${response.status}`);
  }

  if (!contentType.includes("application/json")) {
    throw new Error(
      `Ожидался JSON, но сервер вернул content-type="${contentType}". Ответ: ${rawText.slice(0, 200)}`
    );
  }

  return JSON.parse(rawText) as T;
}