export async function copyText(text: string): Promise<void> {
  await navigator.clipboard.writeText(text);
}

export function downloadLuaFile(code: string, filename = "generated.lua"): void {
  const blob = new Blob([code], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  URL.revokeObjectURL(url);
}