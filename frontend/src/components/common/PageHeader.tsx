interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <div className="page-header">
      <div>
        <div className="page-header__title">{title}</div>
        {subtitle && <div className="page-header__subtitle">{subtitle}</div>}
      </div>

      {actions && <div className="page-header__actions">{actions}</div>}
    </div>
  );
}