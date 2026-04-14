function renderValue(value: unknown): React.ReactNode {
  if (value === null) return <span className="json-viewer__primitive">null</span>;
  if (value === undefined) return <span className="json-viewer__primitive">undefined</span>;

  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return <span className="json-viewer__primitive">{String(value)}</span>;
  }

  if (Array.isArray(value)) {
    return (
      <div className="json-viewer__array">
        {value.length === 0 ? (
          <div className="json-viewer__empty">[]</div>
        ) : (
          value.map((item, index) => (
            <div key={index} className="json-viewer__row">
              <div className="json-viewer__key">[{index}]</div>
              <div className="json-viewer__value">{renderValue(item)}</div>
            </div>
          ))
        )}
      </div>
    );
  }

  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    return (
      <div className="json-viewer__object">
        {entries.length === 0 ? (
          <div className="json-viewer__empty">{`{}`}</div>
        ) : (
          entries.map(([key, val]) => (
            <div key={key} className="json-viewer__row">
              <div className="json-viewer__key">{key}</div>
              <div className="json-viewer__value">{renderValue(val)}</div>
            </div>
          ))
        )}
      </div>
    );
  }

  return <span className="json-viewer__primitive">{String(value)}</span>;
}

export function JsonDetailsViewer({
  title,
  raw,
}: {
  title: string;
  raw: string | null | undefined;
}) {
  if (!raw) return null;

  let parsed: unknown = raw;
  try {
    parsed = JSON.parse(raw);
  } catch {
    parsed = raw;
  }

  return (
    <details className="details-block">
      <summary className="details-block__summary">{title}</summary>
      <div className="details-block__content">
        {typeof parsed === "string" ? (
          <pre className="details-block__pre">{parsed}</pre>
        ) : (
          <div className="json-viewer">{renderValue(parsed)}</div>
        )}
      </div>
    </details>
  );
}