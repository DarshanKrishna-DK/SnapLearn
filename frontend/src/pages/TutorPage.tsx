import { useCallback, useState } from 'react';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';
import { apiClient, handleAPIError } from '@/lib/api';
import type { ExplanationResponse } from '@/types';
import { useAppState } from '@/context/AppStateContext';
import { PixelButton } from '@/components/PixelButton';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ChalkBlackboard } from '@/components/ChalkBlackboard';
import { MermaidDiagrams } from '@/components/MermaidDiagrams';

export function TutorPage() {
  const { studentId, gradeLevel, language } = useAppState();
  const [q, setQ] = useState('');
  const [ex, setEx] = useState<ExplanationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [playAll, setPlayAll] = useState(true);
  const [showRaw, setShowRaw] = useState(false);

  const run = useCallback(async () => {
    const t = q.trim();
    if (!t) {
      toast.error('Enter a question first.');
      return;
    }
    setLoading(true);
    setEx(null);
    setActiveStep(0);
    try {
      const res = await apiClient.explain({
        question: t,
        student_id: studentId,
        grade_level: gradeLevel,
        language,
      });
      setEx(res);
      toast.success('Explanation ready');
    } catch (e) {
      toast.error(handleAPIError(e));
    } finally {
      setLoading(false);
    }
  }, [q, studentId, gradeLevel, language]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <h1 className="font-pixel text-xs text-cream-100">TUTOR</h1>
      <p className="mt-1 text-sm text-cream-200/80 font-body">
        Ask in natural language. The tutor returns a structured lesson with a chalkboard sequence, diagrams, and
        step timing. Your student id, level, and language from Profile shape how the system tracks and adapts follow-up
        sessions.
      </p>
      <div className="mt-6 sl-plate rounded-2xl p-4 sm:p-6">
        <label className="block font-pixel text-[0.45rem] text-cream-200/80">QUESTION</label>
        <textarea
          className="mt-2 w-full min-h-[120px] rounded border border-cream-200/15 bg-maroon-900/50 px-3 py-2 text-sm text-cream-100 font-body focus:outline-none focus:ring-2 focus:ring-gold-400/50"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <PixelButton onClick={run} disabled={loading} variant="solid" type="button">
            {loading ? 'RUNNING' : 'RUN EXPLAIN'}
          </PixelButton>
        </div>
      </div>
      {loading && (
        <div className="mt-6 flex items-center gap-2 text-cream-200/70">
          <LoadingSpinner className="h-6 w-6" />
          <span className="font-mono text-xs">Waiting for the API</span>
        </div>
      )}
      {ex && (
        <div className="mt-8 space-y-6">
          <div className="sl-plate rounded-2xl p-5 sm:p-6">
            <h2 className="font-pixel text-[0.6rem] text-cream-100">EXPLANATION</h2>
            <div className="md-body mt-3 text-sm leading-relaxed text-cream-200/90 font-body">
              <ReactMarkdown>{ex.explanation_text}</ReactMarkdown>
            </div>
          </div>
          <div>
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <h2 className="font-pixel text-[0.6rem] text-cream-100">LIVE CHALKBOARD</h2>
              <label className="flex items-center gap-2 font-mono text-[0.5rem] text-cream-200/70">
                <input
                  type="checkbox"
                  checked={playAll}
                  onChange={(e) => setPlayAll(e.target.checked)}
                />
                Auto-advance steps
              </label>
            </div>
            {ex.board_script?.steps?.length > 0 ? (
              <ChalkBlackboard
                script={ex.board_script}
                activeIndex={activeStep}
                onIndexChange={setActiveStep}
                autoPlayAll={playAll}
              />
            ) : (
              <p className="text-sm text-cream-200/60 font-body">No board steps in this response.</p>
            )}
            {ex.mermaid_diagrams && ex.mermaid_diagrams.length > 0 ? <MermaidDiagrams diagrams={ex.mermaid_diagrams} /> : null}
            <p className="mt-2 text-xs text-cream-200/50 font-mono">
              Timing uses each step&apos;s <code>draw_duration_ms</code> when the API provides it. Total plan:{' '}
              {ex.board_script.total_duration_ms} ms
            </p>
            <button
              type="button"
              className="mt-2 font-mono text-[0.5rem] text-amber-200/90 underline"
              onClick={() => setShowRaw((r) => !r)}
            >
              {showRaw ? 'HIDE' : 'SHOW'} raw step text
            </button>
            {showRaw && ex.board_script.steps[activeStep] && (
              <pre className="mt-2 sl-plate max-h-48 overflow-auto rounded-lg p-3 text-left text-xs text-cream-200/80 font-mono">
                {ex.board_script.steps[activeStep].content}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
