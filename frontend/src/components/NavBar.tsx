import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/voice", label: "Voice" },
  { to: "/upload", label: "Upload" },
  { to: "/tax", label: "Tax Wizard" },
  { to: "/portfolio", label: "Portfolio X-Ray" },
  { to: "/news", label: "News" },
  { to: "/report", label: "Report" },
];

export function NavBar() {
  return (
    <header className="top-nav">
      <h1>ET Money Mentor - Dev1 Build</h1>
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
