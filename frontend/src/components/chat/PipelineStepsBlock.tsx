export function PipelineStepsBlock({ steps }: { steps: any[] }) {
  if (!steps?.length) return null;

  return (
    <details className="mt-3 rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
      <summary className="cursor-pointer text-sm font-medium">
        Шаги генерации
      </summary>

      <div className="mt-2 space-y-2 text-sm">
        {steps.map((s, i) => (
          <div key={i} className="flex justify-between">
            <span className="text-neutral-400">{s.name}</span>
            <span className="text-neutral-500">{s.status}</span>
          </div>
        ))}
      </div>
    </details>
  );
}