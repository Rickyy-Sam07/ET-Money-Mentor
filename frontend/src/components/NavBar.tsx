import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/onboarding", label: "Onboarding" },
  { to: "/voice", label: "Voice" },
  { to: "/upload", label: "Upload" },
  { to: "/tax", label: "Tax Wizard" },
  { to: "/portfolio", label: "Portfolio X-Ray" },
  { to: "/news", label: "News" },
  { to: "/life-event", label: "Life Event" },
  { to: "/couple", label: "Couple Planner" },
  { to: "/whatif", label: "What-If" },
  { to: "/emergency", label: "Emergency" },
  { to: "/recommendations", label: "Recommendations" },
];

export function NavBar() {
  return (
    <header className="top-nav">
      <h1>ET Money Mentor</h1>
      <nav>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
