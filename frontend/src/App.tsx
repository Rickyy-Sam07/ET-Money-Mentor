import { Navigate, Route, Routes } from "react-router-dom";
import { NavBar } from "./components/NavBar";
import { DashboardPage } from "./pages/DashboardPage";
import { NewsPage } from "./pages/NewsPage";
import { PortfolioPage } from "./pages/PortfolioPage";
import { TaxPage } from "./pages/TaxPage";
import { UploadPage } from "./pages/UploadPage";
import { VoicePage } from "./pages/VoicePage";

export default function App() {
  return (
    <div className="app-shell">
      <NavBar />
      <main className="page-shell">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/voice" element={<VoicePage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/tax" element={<TaxPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
