import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "@/components/app-shell";
import { Toaster } from "@/components/ui/toaster";
import DashboardPage from "@/pages/dashboard";
import ScopePage from "@/pages/scope";
import NotFoundPage from "@/pages/not-found";
import PlaceholderPage from "@/pages/placeholder";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route index element={<DashboardPage />} />
          <Route path="scope" element={<ScopePage />} />
          <Route
            path="findings"
            element={<PlaceholderPage title="Findings" />}
          />
          <Route path="reports" element={<PlaceholderPage title="Reports" />} />
          <Route path="404" element={<NotFoundPage />} />
          <Route path="*" element={<Navigate to="/404" replace />} />
        </Route>
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}
