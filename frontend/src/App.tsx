import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastProvider, ToastViewport } from '@/components/ui/toast';
import { SettingsProvider } from '@/hooks/useSettings';
import { VoiceProvider } from '@/hooks/useVoice';
import { AppShell } from '@/components/layout/AppShell';
import { DashboardPage } from '@/pages/DashboardPage';
import { SeePage } from '@/pages/SeePage';
import { ReadPage } from '@/pages/ReadPage';
import { FormPage } from '@/pages/FormPage';
import { AskPage } from '@/pages/AskPage';
import { VoicePage } from '@/pages/VoicePage';
import { ChatPage } from '@/pages/ChatPage';
import { SettingsPage } from '@/pages/SettingsPage';
import { queryClient } from '@/services/queryClient';
import './index.css';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route element={<AppShell />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/see" element={<SeePage />} />
        <Route path="/read" element={<ReadPage />} />
        <Route path="/form" element={<FormPage />} />
        <Route path="/ask" element={<AskPage />} />
        <Route path="/voice" element={<VoicePage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <SettingsProvider>
          <VoiceProvider>
            <ToastProvider>
              <AppRoutes />
              <ToastViewport />
            </ToastProvider>
          </VoiceProvider>
        </SettingsProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;