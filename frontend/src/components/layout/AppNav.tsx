import { NavLink } from "react-router-dom";

const navItems = [
  { to: "/chat", label: "Chat" },
  { to: "/generate", label: "Generate" },
  { to: "/validate", label: "Validate" },
  { to: "/evaluate", label: "Evaluate" },
];

export function AppNav() {
  return (
    <aside className="app-nav">
      <div className="app-nav__brand">
        <div className="app-nav__badge">MTC</div>
        <div>
          <div className="app-nav__title">LocalScript AI</div>
          <div className="app-nav__subtitle">True Tech Hack</div>
        </div>
      </div>

      <nav className="app-nav__menu">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `app-nav__link ${isActive ? "app-nav__link--active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}