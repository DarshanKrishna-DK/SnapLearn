import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { useAppState } from './context/AppStateContext';
import { HomePage } from './pages/HomePage';
import { HubPage } from './pages/HubPage';
import { TutorPage } from './pages/TutorPage';
import { VideoPage } from './pages/VideoPage';
import { QuizPage } from './pages/QuizPage';
import { ProfilePage } from './pages/ProfilePage';
import { SdkPage } from './pages/SdkPage';
import { NotFoundPage } from './pages/NotFoundPage';

function ApiBanner() {
  const { apiOnline, refreshApi, checking } = useAppState();
  if (checking) {
    return (
      <div className="h-0.5 w-full animate-pulse bg-gold-400/40" role="status" aria-label="Checking API" />
    );
  }
  if (apiOnline) return null;
  return (
    <div
      className="border-b border-amber-400/30 bg-amber-950/90 px-3 py-2 text-center text-xs text-amber-100 font-body"
      role="status"
    >
      API unreachable at <code className="text-cream-100/90">/api</code> via Vite proxy. Start the FastAPI app on
      port 8000, then
      <button
        type="button"
        className="ml-1 underline decoration-gold-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400"
        onClick={refreshApi}
      >
        retry
      </button>
      . Navigation in this app still works.
    </div>
  );
}

export default function App() {
  return (
    <>
      <ApiBanner />
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/hub" element={<HubPage />} />
          <Route path="/tutor" element={<TutorPage />} />
          <Route path="/video" element={<VideoPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/test" element={<QuizPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/sdk" element={<SdkPage />} />
          <Route path="/app" element={<Navigate to="/hub" replace />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AppShell>
    </>
  );
}
