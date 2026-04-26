import { useCallback, useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { apiClient, handleAPIError, type LearningProfilePayload } from '@/lib/api';
import { useAppState } from '@/context/AppStateContext';
import { PixelButton } from '@/components/PixelButton';
import { LoadingSpinner } from '@/components/LoadingSpinner';

export function ProfilePage() {
  const { studentId, setStudentId, gradeLevel, setGradeLevel, language, setLanguage, profileRevision } = useAppState();
  const [idInput, setIdInput] = useState(studentId);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<LearningProfilePayload | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    apiClient
      .getStudentProfile(studentId, gradeLevel)
      .then(setData)
      .catch((e) => toast.error(handleAPIError(e)))
      .finally(() => setLoading(false));
  }, [studentId, gradeLevel]);

  useEffect(() => {
    setIdInput(studentId);
  }, [studentId]);

  useEffect(() => {
    void load();
  }, [load, profileRevision]);

  if (loading && !data) {
    return (
      <div className="py-20 flex flex-col items-center">
        <LoadingSpinner />
        <p className="mt-2 font-mono text-xs">Loading</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="font-pixel text-xs">PROFILE</h1>
      <p className="text-sm text-cream-200/80 font-body">
        Learner model the tutor and quiz use: style, accuracy, strengths, and focus areas. Use{' '}
        <code className="text-cream-100/80">presentation-demo</code> for the preloaded high-school example.
      </p>
      <p className="mt-3 text-xs text-cream-200/60 font-body leading-relaxed">
        View this profile as JSON from the API:{' '}
        <a
          className="text-gold-400/90 underline decoration-gold-400/30 underline-offset-2"
          href={`http://127.0.0.1:8000/api/student/${encodeURIComponent(studentId)}/profile`}
          target="_blank"
          rel="noreferrer"
        >
          open <code className="text-[0.8em] text-cream-200/90">/api/student/…/profile</code>
        </a>
        . The same data is persisted under{' '}
        <code className="text-[0.8em] text-cream-200/80">backend/student_profiles/{studentId}.json</code> when the
        server has written a file for that id.
      </p>
      <div className="mt-6 sl-plate p-5 rounded-2xl space-y-4">
        <div>
          <label className="font-pixel text-[0.45rem]">STUDENT ID</label>
          <div className="mt-1 flex flex-wrap gap-2">
            <input
              className="flex-1 min-w-[8rem] rounded border border-cream-200/15 bg-maroon-900/50 px-3 py-2 text-cream-100"
              value={idInput}
              onChange={(e) => setIdInput(e.target.value)}
            />
            <PixelButton
              type="button"
              onClick={() => {
                if (idInput.trim()) {
                  setStudentId(idInput.trim());
                  toast.success('Saved');
                }
              }}
              variant="solid"
            >
              APPLY
            </PixelButton>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="font-pixel text-[0.45rem]">LEVEL</label>
            <select
              className="mt-1 w-full rounded border border-cream-200/15 bg-maroon-900/50 px-2 py-2 text-sm"
              value={gradeLevel}
              onChange={(e) => setGradeLevel(e.target.value as typeof gradeLevel)}
            >
              {(['K', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] as const).map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="font-pixel text-[0.45rem]">LANGUAGE</label>
            <select
              className="mt-1 w-full rounded border border-cream-200/15 bg-maroon-900/50 px-2 py-2 text-sm"
              value={language}
              onChange={(e) => setLanguage(e.target.value as typeof language)}
            >
              {(['en', 'kn', 'hi', 'es', 'fr', 'de', 'zh', 'ja'] as const).map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
        <PixelButton
          type="button"
          variant="ghost"
          onClick={async () => {
            if (!window.confirm('Reset learning data and session flags for this student?')) return;
            try {
              await apiClient.resetStudent(studentId);
              toast.success('Reset complete');
              load();
            } catch (e) {
              toast.error(handleAPIError(e));
            }
          }}
        >
          RESET DATA
        </PixelButton>
      </div>
      {data && (
        <div className="mt-8 space-y-4">
          <div className="sl-plate p-5 rounded-2xl border border-cream-200/10">
            <h2 className="font-pixel text-[0.55rem] text-cream-100">LEARNER SNAPSHOT</h2>
            <dl className="mt-3 grid gap-2 text-sm font-body text-cream-200/90">
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Level (profile)</dt>
                <dd className="font-mono text-cream-100">{data.grade}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Learning style</dt>
                <dd className="font-mono text-cream-100">{data.learning_style}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Quiz accuracy (rolling)</dt>
                <dd className="font-mono text-gold-400">{(data.quiz_accuracy * 100).toFixed(0)}%</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Quizzes completed</dt>
                <dd className="font-mono text-cream-100">{data.total_quizzes}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Time on platform (min)</dt>
                <dd className="font-mono text-cream-100">{data.total_learning_time_minutes}</dd>
              </div>
              <div className="flex flex-wrap justify-between gap-2">
                <dt className="text-cream-200/60">Next difficulty band</dt>
                <dd className="font-mono text-cream-100">{data.recommended_difficulty}</dd>
              </div>
            </dl>
          </div>
          {data.strengths?.length ? (
            <div className="sl-plate p-5 rounded-2xl border border-cream-200/10">
              <h2 className="font-pixel text-[0.5rem] text-cream-100/90">STRENGTHS</h2>
              <ul className="mt-2 list-inside list-disc text-sm text-cream-200/90 font-body">
                {data.strengths.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {data.weaknesses?.length ? (
            <div className="sl-plate p-5 rounded-2xl border border-gold-400/15">
              <h2 className="font-pixel text-[0.5rem] text-gold-400/90">FOCUS AREAS</h2>
              <ul className="mt-2 list-inside list-disc text-sm text-cream-200/90 font-body">
                {data.weaknesses.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {data.recent_quiz_history?.length ? (
            <div className="sl-plate p-4 rounded-2xl font-mono text-[0.65rem] text-cream-200/70 max-h-48 overflow-auto">
              <p className="text-[0.5rem] font-pixel text-cream-200/50 mb-1">RECENT ASSESSMENTS</p>
              <pre className="whitespace-pre-wrap break-all text-[0.6rem] leading-relaxed">
                {JSON.stringify(data.recent_quiz_history, null, 2)}
              </pre>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
