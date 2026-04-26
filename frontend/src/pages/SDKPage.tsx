import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../utils/api';

const codeExamples: Record<string, { install: string; setup: string; usage: string }> = {
  javascript: {
    install: 'npm install @snaplearn/sdk',
    setup: "import { SnapLearnClient } from '@snaplearn/sdk';\nconst client = new SnapLearnClient({ baseUrl: '' });",
    usage: `const res = await client.explain({ question, student_id, grade_level, language });`,
  },
  python: {
    install: 'pip install snaplearn-client',
    setup: 'from snaplearn import Client\nclient = Client(base_url="")',
    usage: 'res = client.explain(question=..., student_id=..., grade_level=..., language=...)',
  },
  curl: {
    install: '# use curl with your local API',
    setup: 'export API=http://localhost:8000',
    usage: 'curl -sS "$API/api/ping"',
  },
};

const apiEndpoints = [
  { method: 'POST' as const, path: '/api/explain', note: 'Tutor and blackboard pipeline' },
  { method: 'POST' as const, path: '/api/generate-video', note: 'Manim render' },
  { method: 'POST' as const, path: '/api/quiz/generate', note: 'Quiz generation' },
  { method: 'GET' as const, path: '/api/student/{id}/profile', note: 'Profile JSON' },
];

const SDKPage: React.FC = () => {
  const [codeLang, setCodeLang] = useState<keyof typeof codeExamples>('javascript');
  const [activeTab, setActiveTab] = useState<'overview' | 'quickstart' | 'api'>('overview');
  const [pingJson, setPingJson] = useState<string | null>(null);
  const [pingErr, setPingErr] = useState<string | null>(null);

  const runPing = async () => {
    setPingErr(null);
    setPingJson(null);
    try {
      const r = await apiClient.healthCheck();
      setPingJson(JSON.stringify(r, null, 2));
    } catch (e) {
      setPingErr((e as Error).message || 'Request failed. Is the backend on port 8000?');
    }
  };

  return (
    <div className="min-h-screen bg-[var(--sl-cream)] text-[#1e1b14]">
      <nav className="border-b border-[#debfc2] bg-white/90">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-4">
          <Link to="/" className="text-xs text-[#8b1538]" style={{ fontFamily: 'var(--font-pixel)' }}>
            SnapLearn
          </Link>
          <div className="flex flex-wrap items-center gap-1 text-sm">
            <Link to="/" className="rounded-md px-2 py-1 text-[#3d3834] hover:bg-[#f5ebe0]">
              Home
            </Link>
            <Link to="/app" className="rounded-md px-2 py-1 text-[#3d3834] hover:bg-[#f5ebe0]">
              App
            </Link>
            <Link to="/docs" className="rounded-md px-2 py-1 text-[#3d3834] hover:bg-[#f5ebe0]">
              Docs
            </Link>
            <span className="px-2 py-1 text-xs font-medium text-[#8b1538]">SDK</span>
          </div>
        </div>
      </nav>

      <section className="border-b border-[#4a0a1c]/10 bg-[#1a0a0f] text-[#fdf5e8]">
        <div className="mx-auto max-w-5xl px-4 py-14">
          <p className="sl-eyebrow text-[#b8a199]">// INTEGRATE SNAPLEARN</p>
          <h1
            className="mt-4 text-sm leading-relaxed text-balance md:text-base"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            HTTP API for explain, video, and quiz. No vanity metrics here, only your running server.
          </h1>
          <p className="mt-4 text-sm text-[#c4a99e]">Same maroon and cream as the product UI. No packaged npm SDK in this repo until you ship one; examples are placeholders for your client.</p>
        </div>
      </section>

      <div className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-8 flex flex-wrap justify-center gap-2">
          {(
            [
              { id: 'overview' as const, label: 'Overview' },
              { id: 'quickstart' as const, label: 'Quick start' },
              { id: 'api' as const, label: 'API' },
            ]
          ).map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setActiveTab(t.id)}
              className={
                'rounded-md border px-4 py-2 text-sm ' +
                (activeTab === t.id
                  ? 'border-[#8b1538] bg-[#8b1538] text-white'
                  : 'border-[#debfc2] bg-white text-[#1e1b14] hover:border-[#8b1538]')
              }
            >
              {t.label}
            </button>
          ))}
        </div>

        {activeTab === 'overview' && (
          <div className="rounded-xl border border-[#debfc2] bg-white p-6">
            <h2 className="text-base font-semibold text-[#1e1b14]">What you wire up</h2>
            <ol className="mt-4 list-decimal pl-5 text-sm text-[#4a433d]">
              <li>Run the FastAPI backend.</li>
              <li>Point the Vite app at the same origin so <span className="font-mono">/api</span> proxies to port 8000.</li>
              <li>Call <span className="font-mono">/api/explain</span>, <span className="font-mono">/api/generate-video</span>, and <span className="font-mono">/api/quiz/*</span> with your student and grade.</li>
            </ol>
          </div>
        )}

        {activeTab === 'quickstart' && (
          <div className="space-y-4 rounded-xl border border-[#debfc2] bg-white p-6">
            <div className="flex flex-wrap gap-2">
              {(Object.keys(codeExamples) as (keyof typeof codeExamples)[]).map((k) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => setCodeLang(k)}
                  className={
                    'rounded border px-3 py-1 text-sm ' +
                    (codeLang === k ? 'border-[#8b1538] bg-[#8b1538] text-white' : 'border-[#debfc2] bg-[#f5ebe0]')
                  }
                >
                  {k}
                </button>
              ))}
            </div>
            <div>
              <h3 className="text-sm font-medium text-[#5c534c]">Install (placeholder name)</h3>
              <pre className="mt-2 overflow-x-auto rounded border border-[#1a0a0f] bg-[#1a0a0f] p-4 text-xs text-[#e8dccf]">
                {codeExamples[codeLang].install}
              </pre>
            </div>
            <div>
              <h3 className="text-sm font-medium text-[#5c534c]">Client</h3>
              <pre className="mt-2 overflow-x-auto rounded border border-[#1a0a0f] bg-[#1a0a0f] p-4 text-xs text-[#e8dccf]">
                {codeExamples[codeLang].setup}
              </pre>
            </div>
            <div>
              <h3 className="text-sm font-medium text-[#5c534c]">Call</h3>
              <pre className="mt-2 overflow-x-auto rounded border border-[#1a0a0f] bg-[#1a0a0f] p-4 text-xs text-[#e8dccf]">
                {codeExamples[codeLang].usage}
              </pre>
            </div>
          </div>
        )}

        {activeTab === 'api' && (
          <div className="space-y-6">
            <div className="rounded-xl border border-[#debfc2] bg-white p-6">
              <h2 className="text-base font-semibold">Endpoints (high level)</h2>
              <ul className="mt-4 space-y-3 text-sm text-[#4a433d]">
                {apiEndpoints.map((e) => (
                  <li key={e.path} className="font-mono text-xs md:text-sm">
                    <span className="text-[#8b1538]">{e.method}</span> {e.path}
                    <span className="block pl-0 text-[#5c534c] md:inline md:pl-2">- {e.note}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-[#debfc2] bg-white p-6">
              <h2 className="text-base font-semibold">Liveness (real request)</h2>
              <p className="mt-2 text-sm text-[#5c534c]">Calls the same <span className="font-mono">/api/ping</span> the app uses. No mock JSON.</p>
              <button
                type="button"
                onClick={runPing}
                className="mt-4 rounded bg-[#8b1538] px-4 py-2 text-sm text-white hover:bg-[#6d0f2b]"
              >
                Run ping
              </button>
              {pingErr && <p className="mt-3 text-sm text-[#6d0f2b]">{pingErr}</p>}
              {pingJson && (
                <pre className="mt-4 max-h-48 overflow-auto rounded border border-[#1a0a0f] bg-[#1a0a0f] p-4 text-xs text-[#a8c7a0]">
                  {pingJson}
                </pre>
              )}
            </div>
          </div>
        )}
      </div>

      <section className="mt-4 border-t border-[#4a0a1c]/10 bg-[#1a0a0f]">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-8 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-[#c4a99e]">Build flows in your product; keep this app as the reference client.</p>
          <div className="flex gap-2">
            <Link
              to="/tutor"
              className="rounded border border-white/20 px-4 py-2 text-sm text-white hover:bg-white/10"
            >
              See tutor
            </Link>
            <Link
              to="/videos"
              className="rounded border border-white/20 px-4 py-2 text-sm text-white hover:bg-white/10"
            >
              See video
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SDKPage;
