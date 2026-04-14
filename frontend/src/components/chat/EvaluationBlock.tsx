export function EvaluationBlock({ report }: { report: any }) {
  if (!report) return null;

  return (
    <details className="mt-3 rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
      <summary className="cursor-pointer text-sm font-medium">
        Детали генерации
      </summary>

      <div className="mt-2 text-sm text-neutral-400 space-y-1">
        <div>Модель: {report.model}</div>
        <div>Провайдер: {report.provider}</div>
        <div>Попыток: {report.attempts}</div>
        <div>Режим: {report.output_mode}</div>
        <div>Профиль: {report.domain_profile}</div>
      </div>
    </details>
  );
}