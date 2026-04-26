import { useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';
import { apiClient, handleAPIError, type LearningProfilePayload } from '@/lib/api';
import { useAppState } from '@/context/AppStateContext';
import { PixelButton } from '@/components/PixelButton';
import { LoadingSpinner } from '@/components/LoadingSpinner';

type QuizQ = { id: string; question: string; options: string[]; topic: string; difficulty: string };
type QuizD = {
  quiz_id: string;
  title: string;
  topic: string;
  grade_level: string;
  difficulty: string;
  time_limit_minutes: number;
  questions: QuizQ[];
};

type SubmitResponse = {
  quiz_results: {
    score_percentage: number;
    total_questions: number;
    correct_answers: number;
    total_time_seconds: number;
    mistakes: Array<Record<string, unknown>>;
  };
  profile_updates: {
    new_accuracy: number;
    total_quizzes: number;
    strengths: string[];
    weaknesses: string[];
  };
  adaptive_feedback: { difficulty_adjustment: string; focus_areas: string[]; next_topics: string[] };
  learner_profile?: LearningProfilePayload;
};

export function QuizPage() {
  const { studentId, gradeLevel, bumpProfile } = useAppState();
  const [topicIn, setTopicIn] = useState('math');
  const [quiz, setQuiz] = useState<QuizD | null>(null);
  const [ix, setIx] = useState(0);
  const [ans, setAns] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [res, setRes] = useState<SubmitResponse | null>(null);
  const [tLeft, setTLeft] = useState(0);
  const [active, setActive] = useState(true);
  const [nQuestions, setNQuestions] = useState<3 | 5 | 10>(5);

  const startQuiz = useCallback(async () => {
    const topic = topicIn.trim() || 'math';
    setLoading(true);
    setDone(false);
    setRes(null);
    setIx(0);
    setAns({});
    setActive(true);
    try {
      const data = (await apiClient.generateQuiz({
        student_id: studentId,
        grade_level: gradeLevel,
        topic,
        difficulty: 'adaptive',
        num_questions: nQuestions,
      })) as QuizD;
      setQuiz(data);
      setTLeft((data.time_limit_minutes || 5) * 60);
    } catch (e) {
      toast.error(handleAPIError(e));
    } finally {
      setLoading(false);
    }
  }, [studentId, gradeLevel, topicIn, nQuestions]);

  const submit = useCallback(async () => {
    if (!quiz) return;
    setActive(false);
    setSubmitting(true);
    try {
      const responses = quiz.questions.map((q) => ({
        question_id: q.id,
        selected_answer: ans[q.id] ?? 0,
        is_correct: false,
        time_taken_seconds: 0,
      }));
      const out = (await apiClient.submitQuiz({
        student_id: studentId,
        grade_level: gradeLevel,
        quiz_id: quiz.quiz_id,
        topic: quiz.topic,
        difficulty: quiz.difficulty,
        responses,
      })) as SubmitResponse;
      setRes(out);
      setDone(true);
      bumpProfile();
      toast.success('Profile updated with this quiz');
    } catch (e) {
      toast.error(handleAPIError(e));
    } finally {
      setSubmitting(false);
    }
  }, [quiz, ans, studentId, gradeLevel, bumpProfile]);

  useEffect(() => {
    if (!active || done || tLeft <= 0 || !quiz) return;
    const id = window.setTimeout(() => setTLeft((s) => s - 1), 1000);
    return () => clearTimeout(id);
  }, [tLeft, done, active, quiz]);

  useEffect(() => {
    if (!quiz || done || submitting || tLeft > 0) return;
    void submit();
  }, [tLeft, quiz, done, submitting, submit]);

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center">
        <LoadingSpinner />
        <p className="mt-2 font-mono text-xs">Building your quiz</p>
      </div>
    );
  }

  if (done && res) {
    const { quiz_results, profile_updates, adaptive_feedback } = res;
    return (
      <div className="mx-auto max-w-2xl px-4 py-10">
        <div className="sl-plate rounded-2xl p-6 sm:p-8">
          <h1 className="font-pixel text-xs">RESULTS</h1>
          <p className="mt-3 text-2xl font-body text-cream-100">
            {quiz_results.correct_answers} / {quiz_results.total_questions} correct
          </p>
          <p className="mt-1 font-mono text-sm text-gold-400">
            {quiz_results.score_percentage.toFixed(1)}%
          </p>
          {profile_updates && (
            <div className="mt-6 text-sm text-cream-200/90 font-body space-y-1">
              <p>
                <span className="text-cream-200/50">Profile accuracy: </span>
                {(profile_updates.new_accuracy * 100).toFixed(0)}% · {profile_updates.total_quizzes} quiz
                {profile_updates.total_quizzes === 1 ? '' : 'zes'}
              </p>
              {res.learner_profile?.last_updated ? (
                <p className="text-xs text-cream-200/50 font-mono">
                  Server profile updated: {new Date(res.learner_profile.last_updated).toLocaleString()}
                </p>
              ) : null}
              {profile_updates.weaknesses?.length ? (
                <p>Focus: {profile_updates.weaknesses.slice(0, 4).join(', ')}</p>
              ) : null}
            </div>
          )}
          {adaptive_feedback?.focus_areas?.length ? (
            <div className="mt-4 text-sm text-cream-200/80 font-body">
              <p className="text-[0.5rem] font-pixel uppercase text-gold-400/70">Areas to review</p>
              <ul className="mt-1 list-inside list-disc">
                {adaptive_feedback.focus_areas.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <PixelButton
            onClick={() => {
              setQuiz(null);
              setDone(false);
              setRes(null);
            }}
            variant="solid"
            type="button"
          >
            NEW QUIZ
          </PixelButton>
        </div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16">
        <h1 className="font-pixel text-xs">ADAPTIVE QUIZ</h1>
        <p className="mt-2 text-sm text-cream-200/80 font-body">
          Enter a topic. Questions are generated on the server using your profile and the Gemini key from the API.
          Finish and submit in one session so the graded run lines up with what you see in Profile afterward.
        </p>
        <p className="mt-3 text-[0.5rem] font-pixel text-cream-200/60">COUNT</p>
        <div className="mt-1 flex flex-wrap gap-2">
          {([3, 5, 10] as const).map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setNQuestions(n)}
              className={`rounded border px-3 py-1.5 font-mono text-xs ${
                nQuestions === n ? 'border-gold-400 bg-maroon-800/60 text-cream-100' : 'border-cream-200/20 text-cream-200/70'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
        <label className="mt-6 block">
          <span className="text-[0.5rem] font-pixel text-cream-300/70">TOPIC</span>
          <input
            value={topicIn}
            onChange={(e) => setTopicIn(e.target.value)}
            className="mt-2 w-full rounded border border-cream-200/20 bg-maroon-950/60 px-3 py-2.5 text-sm text-cream-100 font-body placeholder:text-cream-200/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400"
            placeholder="e.g. fractions, solar system, reading"
            autoComplete="off"
          />
        </label>
        <div className="mt-5">
          <PixelButton type="button" variant="solid" onClick={startQuiz}>
            GENERATE
          </PixelButton>
        </div>
        <p className="mt-4 text-xs text-cream-200/50 font-mono">Student: {studentId} · level {gradeLevel}</p>
      </div>
    );
  }

  const qn = quiz.questions[ix];
  if (!qn) {
    return null;
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <div className="flex items-center justify-between">
        <h1 className="font-pixel text-[0.65rem]">QUIZ</h1>
        <span className="font-mono text-xs text-gold-400">{tLeft}s</span>
      </div>
      <p className="text-sm text-cream-200/70 font-body mt-1">
        {quiz.title} · {quiz.topic}
      </p>
      <div className="mt-6 sl-plate p-5 rounded-2xl" style={{ transform: 'rotate(-0.2deg)' }}>
        <p className="font-body text-cream-100/90 text-sm sm:text-base">{qn.question}</p>
        <ul className="mt-4 space-y-2">
          {qn.options.map((o, oi) => (
            <li key={`${qn.id}-${oi}`}>
              <button
                type="button"
                onClick={() => setAns((a) => ({ ...a, [qn.id]: oi }))}
                className={`w-full text-left rounded border px-3 py-2 text-sm font-body ${
                  ans[qn.id] === oi ? 'border-gold-400 bg-maroon-800/60' : 'border-cream-200/20'
                } focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400`}
              >
                {o}
              </button>
            </li>
          ))}
        </ul>
        <div className="mt-4 flex flex-wrap gap-2">
          <PixelButton
            type="button"
            variant="ghost"
            onClick={() => setIx((i) => Math.max(0, i - 1))}
            disabled={ix === 0}
          >
            PREV
          </PixelButton>
          <PixelButton
            type="button"
            variant="ghost"
            onClick={() => setIx((i) => Math.min(quiz.questions.length - 1, i + 1))}
            disabled={ix >= quiz.questions.length - 1}
          >
            NEXT
          </PixelButton>
          {ix === quiz.questions.length - 1 && (
            <PixelButton type="button" onClick={submit} disabled={submitting} variant="solid">
              SUBMIT
            </PixelButton>
          )}
        </div>
      </div>
    </div>
  );
}
