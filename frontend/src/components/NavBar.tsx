// [DEV1] NavBar.tsx — shared nav. Dev2: add your nav links to the links array below.
import { NavLink } from "react-router-dom";

const sections = [
  {
    heading: "Core",
    links: [
      { to: "/", label: "Dashboard", short: "DB", icon: "HM" },
      { to: "/onboarding", label: "Onboarding", short: "ON", icon: "OB" },
      { to: "/voice", label: "Voice Hub", short: "VC", icon: "VH" },
      { to: "/upload", label: "Upload", short: "UP", icon: "UL" },
      { to: "/report", label: "Report", short: "RP", icon: "RP" },
    ],
  },
  {
    heading: "Analysis",
    links: [
      { to: "/tax", label: "Tax Wizard", short: "TX", icon: "TX" },
      { to: "/portfolio", label: "Portfolio X-Ray", short: "PF", icon: "PX" },
      { to: "/news", label: "News Radar", short: "NW", icon: "NR" },
      { to: "/recommendations", label: "Recommendations", short: "RC", icon: "RC" },
    ],
  },
  {
    heading: "Life Planning",
    links: [
      { to: "/life-event", label: "Life Event", short: "LE", icon: "LE" },
      { to: "/couple", label: "Couple Planner", short: "CP", icon: "CP" },
      { to: "/whatif", label: "What-If Simulator", short: "WI", icon: "WF" },
      { to: "/emergency", label: "Emergency", short: "EM", icon: "EM" },
    ],
  },
];

type NavBarProps = {
  collapsed: boolean;
  onToggle: () => void;
};

export function NavBar({ collapsed, onToggle }: NavBarProps) {
  return (
    <aside className={`side-nav ${collapsed ? "side-nav-collapsed" : ""}`}>
      <div className="side-nav-brand">
        <button type="button" className="side-nav-toggle" onClick={onToggle} aria-label="Toggle sidebar">
          {collapsed ? ">>" : "<<"}
        </button>
        <p className="side-nav-kicker">ET MONEY MENTOR</p>
        <h1>Advisor Workspace</h1>
      </div>

      <nav className="side-nav-sections" aria-label="Primary">
        {sections.map((section) => (
          <section key={section.heading} className="side-nav-section">
            <p className="side-nav-heading">{section.heading}</p>
            {section.links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  isActive ? "nav-link nav-link-active" : "nav-link"
                }
                title={link.label}
              >
                <span className="nav-badge" aria-hidden>
                  {link.icon}
                </span>
                <span className="nav-label">{link.label}</span>
              </NavLink>
            ))}
          </section>
        ))}
      </nav>
    </aside>
  );
}
