import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider, useLanguage } from "@/contexts/LanguageContext";
import LanguageSelection from "@/components/LanguageSelection";
import BottomNav from "@/components/BottomNav";
import HomePage from "@/pages/HomePage";
import RecommendPage from "@/pages/RecommendPage";
import ResultsPage from "@/pages/ResultsPage";
import SpoilagePage from "@/pages/SpoilagePage";
import MarketsPage from "@/pages/MarketsPage";
import ProfilePage from "@/pages/ProfilePage";
import NotFound from "@/pages/NotFound";
import InsightsPage from '@/pages/InsightsPage';
const queryClient = new QueryClient();

const AppContent = () => {
  const { hasSelectedLanguage } = useLanguage();

  if (!hasSelectedLanguage) {
    return <LanguageSelection />;
  }

  return (
    <BrowserRouter>
      <BottomNav />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/recommend" element={<RecommendPage />} />
        <Route path="/results" element={<ResultsPage />} />
        <Route path="/spoilage" element={<SpoilagePage />} />
        <Route path="/markets" element={<MarketsPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <LanguageProvider>
        <AppContent />
      </LanguageProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
