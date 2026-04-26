import { motion } from 'framer-motion';
import { PixelButton } from '@/components/PixelButton';
import { useAppState } from '@/context/AppStateContext';

const rows = [
  { to: '/tutor', title: 'AI TUTOR', desc: 'Structured lessons with chalkboard steps and diagrams (e.g. matrices, factorials).', tag: 'POST /api/lesson/structured' },
  { to: '/video', title: 'MANIM VIDEO', desc: 'Request a topic, duration, and optional speech track through the video route.', tag: 'POST /api/generate-video' },
  { to: '/quiz', title: 'ADAPTIVE QUIZ', desc: 'Generate and submit a quiz for your current student id and grade level.', tag: 'POST /api/quiz/*' },
  { to: '/profile', title: 'PROFILE', desc: 'Read server-side profile, topics, and stats for the active student id.', tag: 'GET /api/student/...' },
] as const;

export function HubPage() {
  const { studentId, gradeLevel, language } = useAppState();
  return (
    <div className="px-4 py-12 max-w-5xl mx-auto">
      <h1 className="font-pixel text-xs text-cream-100">HUB</h1>
      <p className="mt-2 text-sm text-cream-200/80 font-body max-w-2xl">
        You are using student id <code className="text-gold-400/90">{studentId}</code>, grade {gradeLevel}, language{' '}
        {language}. Adjust these in the profile view or the home page band.
      </p>
      <ul className="mt-8 space-y-0 border border-cream-200/10 rounded-2xl overflow-hidden divide-y divide-cream-200/10">
        {rows.map((r, i) => (
          <li key={r.to}>
            <motion.div
              className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"
              style={{ background: i % 2 ? 'linear-gradient(90deg, #1a050c, #120308)' : 'linear-gradient(90deg, #120308, #1a050c)' }}
              whileHover={{ x: 4 }}
            >
              <div>
                <div className="font-mono text-[0.5rem] text-gold-400/70">{r.tag}</div>
                <h2 className="font-pixel text-[0.6rem] mt-1 text-cream-100">{r.title}</h2>
                <p className="text-sm text-cream-200/80 font-body max-w-md mt-1">{r.desc}</p>
              </div>
              <PixelButton to={r.to} variant="solid">
                OPEN
              </PixelButton>
            </motion.div>
          </li>
        ))}
      </ul>
      <div className="mt-8 p-4 sl-plate rounded-2xl">
        <h3 className="font-pixel text-[0.5rem] text-cream-100">API DOCS (RUNNING SERVER)</h3>
        <p className="text-sm text-cream-200/80 font-body mt-1">
          Open the interactive OpenAPI UI in a new tab. It is served from the same FastAPI app as the API routes.
        </p>
        <a
          href="http://127.0.0.1:8000/docs"
          className="mt-3 inline-block text-[0.5rem] font-pixel text-gold-400 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400"
          target="_blank"
          rel="noreferrer"
        >
          127.0.0.1:8000/docs
        </a>
      </div>
    </div>
  );
}
