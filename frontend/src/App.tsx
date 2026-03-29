// [DEV1] App.tsx — routing shell. Dev2: add your routes here, do not remove existing ones.
import { useMemo, useState } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { VoiceCommandCenter } from "./components/VoiceCommandCenter";
import { DashboardPage } from "./pages/DashboardPage";
import { NewsPage } from "./pages/NewsPage";
import { PortfolioPage } from "./pages/PortfolioPage";
import { ReportPage } from "./pages/ReportPage";
import { TaxPage } from "./pages/TaxPage";
import { UploadPage } from "./pages/UploadPage";
import { VoicePage } from "./pages/VoicePage";
// Dev2 pages
import { OnboardingPage } from "./pages/OnboardingPage";
import { LifeEventPage } from "./pages/LifeEventPage";
import { CouplePlannerPage } from "./pages/CouplePlannerPage";
import { WhatIfPage } from "./pages/WhatIfPage";
import { EmergencyPage } from "./pages/EmergencyPage";
import { RecommendationsPage } from "./pages/RecommendationsPage";

const ROUTE_LABELS: Record<string, string> = {
  "/": "Dashboard",
  "/onboarding": "Onboarding",
  "/voice": "Voice Hub",
  "/upload": "Upload",
  "/tax": "Tax Wizard",
  "/portfolio": "Portfolio X-Ray",
  "/news": "News Radar",
  "/report": "Report",
  "/life-event": "Life Event",
  "/couple": "Couple Planner",
  "/whatif": "What-If Simulator",
  "/emergency": "Emergency",
  "/recommendations": "Recommendations",
};

export default function App() {
  const [navCollapsed, setNavCollapsed] = useState(false);
  const location = useLocation();

  const currentPageTitle = ROUTE_LABELS[location.pathname] ?? "Dashboard";
  const breadcrumb = useMemo(() => {
    const pieces = location.pathname.split("/").filter(Boolean);
    if (!pieces.length) {
      return ["Workspace", "Dashboard"];
    }
    return ["Workspace", ...pieces.map((part) => part.replace(/-/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase()))];
  }, [location.pathname]);

  return (
    <div className={`app-shell ${navCollapsed ? "app-shell-collapsed" : ""}`}>
      <NavBar collapsed={navCollapsed} onToggle={() => setNavCollapsed((value) => !value)} />
      <div className="workspace-shell">
        <header className="workspace-header">
          <p className="workspace-kicker">Personal Finance OS</p>
          <h2>{currentPageTitle}</h2>
          <p className="workspace-breadcrumb">{breadcrumb.join(" / ")}</p>
        </header>
        <main className="page-shell">
          <VoiceCommandCenter />
          <div key={location.pathname} className="route-stage">
            <Routes>
              {/* Dev1 pages */}
              <Route path="/" element={<DashboardPage />} />
              <Route path="/voice" element={<VoicePage />} />
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/tax" element={<TaxPage />} />
              <Route path="/portfolio" element={<PortfolioPage />} />
              <Route path="/news" element={<NewsPage />} />
              <Route path="/report" element={<ReportPage />} />
              {/* Dev2 pages */}
              <Route path="/onboarding" element={<OnboardingPage />} />
              <Route path="/life-event" element={<LifeEventPage />} />
              <Route path="/couple" element={<CouplePlannerPage />} />
              <Route path="/whatif" element={<WhatIfPage />} />
              <Route path="/emergency" element={<EmergencyPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}
