export function DiffBlock({ diff }: { diff?: string }) {
  if (!diff) return null;

  return (
    <details className="mt-3 rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
      <summary className="cursor-pointer text-sm font-medium">
        Изменения (diff)
      </summary>

      <pre className="mt-2 text-xs overflow-x-auto whitespace-pre-wrap text-neutral-300">
        {diff}
      </pre>
    </details>
  );
}