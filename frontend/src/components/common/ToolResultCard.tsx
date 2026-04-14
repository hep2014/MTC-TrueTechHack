interface ToolResultCardProps {
  title: string;
  children: React.ReactNode;
}

export function ToolResultCard({ title, children }: ToolResultCardProps) {
  return (
    <section className="tool-result-card">
      <div className="tool-result-card__title">{title}</div>
      <div className="tool-result-card__body">{children}</div>
    </section>
  );
}