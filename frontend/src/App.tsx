import { Navigate, Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { DashboardPage } from "./pages/DashboardPage";
import { NewsPage } from "./pages/NewsPage";
import { PortfolioPage } from "./pages/PortfolioPage";
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

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      <main className="page-shell">
        <Routes>
          {/* Dev1 pages */}
          <Route path="/" element={<DashboardPage />} />
          <Route path="/voice" element={<VoicePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/tax" element={<TaxPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/news" element={<NewsPage />} />
          {/* Dev2 pages */}
          <Route path="/onboarding" element={<OnboardingPage />} />
          <Route path="/life-event" element={<LifeEventPage />} />
          <Route path="/couple" element={<CouplePlannerPage />} />
          <Route path="/whatif" element={<WhatIfPage />} />
          <Route path="/emergency" element={<EmergencyPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
