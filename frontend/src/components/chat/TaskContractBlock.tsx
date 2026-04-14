export function TaskContractBlock({ contract }: { contract: any }) {
  if (!contract) return null;

  return (
    <details className="mt-3 rounded-xl border border-neutral-800 bg-neutral-900/60 p-3">
      <summary className="cursor-pointer text-sm font-medium">
        Контракт задачи
      </summary>

      <div className="mt-2 text-sm space-y-1 text-neutral-300">
        <div><b>Цель:</b> {contract.goal}</div>
        <div><b>Тип:</b> {contract.task_type}</div>
        <div><b>Подтип:</b> {contract.task_subtype}</div>
        <div><b>Runtime:</b> {contract.target_runtime}</div>
      </div>
    </details>
  );
}