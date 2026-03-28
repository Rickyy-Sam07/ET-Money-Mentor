// [DEV1] App.tsx — routing shell. Dev2: add your routes here, do not remove existing ones.
import { Navigate, Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { VoiceCommandCenter } from "./components/VoiceCommandCenter";
import { DashboardPage } from "./pages/DashboardPage";
import { NewsPage } from "./pages/NewsPage";
import { PortfolioPage } from "./pages/PortfolioPage";
import { ReportPage } from "./pages/ReportPage";
import { TaxPage } from "./pages/TaxPage";
import { UploadPage } from "./pages/UploadPage";
import { VoicePage } from "./pages/VoicePage";

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      <main className="page-shell">
        <VoiceCommandCenter />
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/voice" element={<VoicePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/tax" element={<TaxPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/report" element={<ReportPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
