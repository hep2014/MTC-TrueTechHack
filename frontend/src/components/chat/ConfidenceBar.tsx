interface ConfidenceBarProps {
  score: number;
}

export function ConfidenceBar({ score }: ConfidenceBarProps) {
  const normalized = Math.max(0, Math.min(100, score));

  return (
    <div className="confidence">
      <div className="confidence__header">
        <span>Уровень уверенности</span>
        <span>{normalized}/100</span>
      </div>
      <div className="confidence__track">
        <div className="confidence__fill" style={{ width: `${normalized}%` }} />
      </div>
    </div>
  );
}