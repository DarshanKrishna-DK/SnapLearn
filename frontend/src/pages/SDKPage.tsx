import { motion } from 'framer-motion';
import { useState } from 'react';
import { PixelButton } from '@/components/PixelButton';

const coreEndpoints = [
  { method: 'POST', path: '/api/lesson/structured', desc: 'Structured lessons with chalkboard, diagrams, and timed response (4 to 10 seconds). Matrices uses a formal track first, then an applied track after a matrices quiz with at least one incorrect answer.' },
  { method: 'POST', path: '/api/video/program', desc: 'Full program metadata with about a one minute pipeline, 7+ minute run length, captions and narration plan, and a short browser preview stream.' },
  { method: 'POST', path: '/api/quiz/generate', desc: 'Gemini generates items from topic, grade, and count (3, 5, or 10). Personalizes from the learner profile.' },
  { method: 'POST', path: '/api/quiz/submit', desc: 'Grades the attempt, updates the profile, and unlocks the alternate matrices teaching track when a matrices quiz has mistakes.' },
  { method: 'GET', path: '/api/student/{id}/profile', desc: 'Learning style, accuracy, strengths, focus areas, and recent assessments.' },
] as const;

const deckEndpoints = [
  { method: 'POST', path: '/api/staging/explain', desc: 'Optional timed pipeline for alternate scripting (internal tooling).' },
  { method: 'POST', path: '/api/staging/generate-video', desc: 'Optional video pipeline for staging environments.' },
  { method: 'POST', path: '/api/staging/generate-quiz', desc: 'Optional quiz path with profile targeting (uses Gemini when configured).' },
  { method: 'GET', path: '/api/staging/student-profile/{id}', desc: 'Profile snapshot for integration tests.' },
  { method: 'POST', path: '/api/staging/reset-demo', desc: 'Resets session flags for a clean run-through.' },
] as const;

const advancedEndpoints = [
  { method: 'GET', path: '/api/analytics/learning/{student_id}', desc: 'Comprehensive learning analytics including velocity tracking, concept mastery, and predictive insights.' },
  { method: 'POST', path: '/api/conversation/start', desc: 'Multi-turn tutoring conversations with context awareness and adaptive dialogue management.' },
  { method: 'POST', path: '/api/assessment/comprehensive', desc: 'Advanced assessment with mistake pattern detection and personalized feedback generation.' },
  { method: 'POST', path: '/api/video/generate-contextual', desc: 'Enhanced video generation with conversation context, quality settings, and animation style preferences.' },
] as const;

const DEMONSTRATION_STEPS = [
  'Start the FastAPI app on port 8000 and keep this Vite app on 3000 (proxy to /api).',
  'Open **Open docs** to show interactive OpenAPI. Expand `POST /api/lesson/structured` or `POST /api/video/program` and **Try it out** with a JSON body (question, student_id, grade_level).',
  'Use the **Core APIs** tab to narrate the contract. Point to **GET /api/student/{id}/profile** and show the JSON in the browser or Swagger.',
  'Click **Test tutor**, **Try quiz**, and **Student profile** to show the same APIs driving the product UI with one student id.',
  'On the **Staging** tab, mention optional integration routes and **Integration UI** if you use the static `sdk_demo` page.',
] as const;

export function SdkPage() {
  const [activeTab, setActiveTab] = useState<'core' | 'deck' | 'advanced'>('core');
  const deckStatus: 'online' | 'offline' | 'testing' = 'online';

  const currentEndpoints = 
    activeTab === 'core' ? coreEndpoints :
    activeTab === 'deck' ? deckEndpoints :
    advancedEndpoints;

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-900 via-neutral-800 to-maroon-900/20">
      <div className="fixed inset-0 opacity-[0.02] pointer-events-none">
        <div 
          className="w-full h-full"
          style={{
            backgroundImage: `
              linear-gradient(90deg, #8B1538 1px, transparent 1px),
              linear-gradient(0deg, #8B1538 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px'
          }}
        />
      </div>

      <div className="relative z-10 px-4 py-10 max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="font-pixel text-2xl text-maroon-400 mb-4">
            SNAPLEARN SDK
          </h1>
          <p className="text-lg text-cream-200/90 font-body max-w-3xl mx-auto mb-6">
            HTTP APIs for structured lessons, video program metadata, adaptive quizzes, and learner profiles. Use the
            list below and Swagger to explore requests and response shapes.
          </p>

          <div className="max-w-3xl mx-auto text-left sl-plate rounded-xl p-5 mb-8 border border-cream-200/10">
            <p className="font-pixel text-[0.5rem] text-gold-400/80 mb-3">DEMONSTRATION (5 MIN)</p>
            <ol className="list-decimal list-inside space-y-2 text-sm text-cream-200/85 font-body leading-relaxed">
              {DEMONSTRATION_STEPS.map((step) => (
                <li key={step} className="marker:text-gold-500/80">
                  {step.split('**').map((part, i) =>
                    i % 2 === 1 ? (
                      <strong key={i} className="text-cream-100/95 font-semibold">
                        {part}
                      </strong>
                    ) : (
                      <span key={i}>{part}</span>
                    )
                  )}
                </li>
              ))}
            </ol>
          </div>

          <div className="flex justify-center gap-8 mb-8 flex-wrap">
            <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 rounded-full px-4 py-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-400">API Online</span>
            </div>
            <div className="flex items-center gap-2 bg-maroon-500/10 border border-maroon-500/20 rounded-full px-4 py-2">
              <div
                className={`w-2 h-2 rounded-full ${
                  deckStatus === 'online' ? 'bg-green-500' : deckStatus === 'testing' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'
                }`}
              />
              <span className="text-sm text-maroon-300">Staging {deckStatus === 'online' ? 'Ready' : deckStatus}</span>
            </div>
          </div>
        </motion.div>

        <div className="flex justify-center mb-8">
          <div className="bg-cream-500/5 border border-cream-500/10 rounded-lg p-1 flex gap-1">
            {(['core', 'deck', 'advanced'] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 rounded-md transition-all text-sm font-medium ${
                  activeTab === tab
                    ? 'bg-maroon-500 text-white shadow-lg'
                    : 'text-cream-400 hover:text-cream-200 hover:bg-cream-500/5'
                }`}
              >
                {tab === 'core' && 'Core APIs'}
                {tab === 'deck' && 'Staging'}
                {tab === 'advanced' && 'Advanced'}
              </button>
            ))}
          </div>
        </div>

        <div className="flex justify-center gap-4 mb-12 flex-wrap">
          <PixelButton 
            href={activeTab === 'deck' ? '/sdk_demo.html' : 'http://127.0.0.1:8000/docs'} 
            variant="solid"
            className="bg-maroon-500 hover:bg-maroon-600"
          >
            {activeTab === 'deck' ? 'INTEGRATION UI' : 'OPEN DOCS'}
          </PixelButton>
          <PixelButton href="/profile" variant="ghost">
            STUDENT PROFILE
          </PixelButton>
          <PixelButton href="/tutor" variant="ghost">
            TEST TUTOR
          </PixelButton>
          <PixelButton href="/quiz" variant="ghost">
            TRY QUIZ
          </PixelButton>
        </div>

        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <ol className="space-y-0 border border-cream-200/10 rounded-2xl overflow-hidden divide-y divide-cream-200/10 list-none p-0">
            {currentEndpoints.map((endpoint, i) => (
              <motion.li
                key={endpoint.path + endpoint.method}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.05 * i }}
                className="p-6 hover:bg-cream-500/5 transition-colors group"
                style={{
                  background: 'linear-gradient(110deg, rgba(139, 21, 56, 0.02) 0%, rgba(245, 241, 232, 0.01) 40%, rgba(0,0,0,0.1) 100%)',
                }}
              >
                <div className="flex flex-wrap items-center gap-3 mb-2">
                  <span className={`font-mono text-xs px-2 py-1 rounded-md font-semibold ${
                    endpoint.method === 'GET' 
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                      : 'bg-maroon-500/20 text-maroon-400 border border-maroon-500/30'
                  }`}>
                    {endpoint.method}
                  </span>
                  <code className="font-mono text-sm text-cream-200/90 break-all">
                    {endpoint.path}
                  </code>
                  {activeTab === 'deck' && (
                    <span className="bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 px-2 py-0.5 rounded-md text-xs font-medium">
                      STAGING
                    </span>
                  )}
                </div>
                <p className="text-sm text-cream-200/70 font-body max-w-4xl leading-relaxed group-hover:text-cream-200/90 transition-colors">
                  {endpoint.desc}
                </p>
              </motion.li>
            ))}
          </ol>
        </motion.div>

        {activeTab === 'core' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-12 grid md:grid-cols-2 gap-8"
          >
            <div className="bg-cream-500/5 border border-cream-500/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-cream-200 mb-4 flex items-center gap-2">
                <span>React</span>
              </h3>
              <div className="bg-neutral-800 rounded-lg p-4 text-sm font-mono">
                <pre className="text-cream-300">
{`import { SnapLearnSDK } from '@snaplearn/react-sdk';

function TutorComponent() {
  const { explainTopic, loading } = SnapLearnSDK({
    apiKey: process.env.SNAPLEARN_API_KEY,
    studentId: 'student_123'
  });

  return (
    <TutorInterface
      onQuestion={explainTopic}
      loading={loading}
      adaptive={true}
    />
  );
}`}
                </pre>
              </div>
            </div>

            <div className="bg-cream-500/5 border border-cream-500/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-cream-200 mb-4 flex items-center gap-2">
                <span>Python</span>
              </h3>
              <div className="bg-neutral-800 rounded-lg p-4 text-sm font-mono">
                <pre className="text-cream-300">
{`import requests

BASE = 'https://your-api.example'
headers = {'X-API-Key': 'your-key'}

# Structured lesson with chalkboard and diagrams
r = requests.post(
    f'{BASE}/api/lesson/structured',
    json={'question': 'What are matrices?', 'student_id': 'presentation-demo', 'grade_level': 10},
    headers=headers,
    timeout=120,
)
explanation = r.json()

# Long-form program (metadata, captions, preview URL)
r2 = requests.post(
    f'{BASE}/api/video/program',
    json={'topic': 'factorials', 'student_id': 'presentation-demo', 'grade_level': 10},
    headers=headers,
    timeout=300,
)
video = r2.json()`}
                </pre>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'deck' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-12 bg-cream-500/5 border border-cream-200/15 rounded-xl p-6"
          >
            <h3 className="text-lg font-semibold text-maroon-300 mb-4">
              Staging and integration
            </h3>
            <div className="space-y-4 text-cream-200/80">
              <p>
                <strong>Environments for QA and client pilots:</strong> The staging routes mirror production behavior with
                controllable timing and sample payloads so teams can validate UIs, auth, and error handling before go-live.
              </p>
              <div className="grid md:grid-cols-3 gap-4 mt-6">
                <div className="bg-maroon-500/10 border border-maroon-500/20 rounded-lg p-4">
                  <h4 className="font-semibold text-maroon-300 mb-2">Tutor and video</h4>
                  <p className="text-sm">End-to-end flows for structured lessons and long-form video metadata with on-screen render states.</p>
                </div>
                <div className="bg-maroon-500/10 border border-maroon-500/20 rounded-lg p-4">
                  <h4 className="font-semibold text-maroon-300 mb-2">Quizzes and profiles</h4>
                  <p className="text-sm">Gemini-backed item generation and profile updates through the same contracts as production.</p>
                </div>
                <div className="bg-maroon-500/10 border border-maroon-500/20 rounded-lg p-4">
                  <h4 className="font-semibold text-maroon-300 mb-2">Session reset</h4>
                  <p className="text-sm">Single-call reset of learner state flags for repeatable review cycles and sales walkthroughs.</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
