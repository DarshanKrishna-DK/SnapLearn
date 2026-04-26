import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { IconChalkboard, IconFilm, IconListCheck, IconBook } from '../components/ui/SlIcons';

const SECTIONS: { id: string; label: string }[] = [
  { id: 'start', label: 'Getting started' },
  { id: 'tutor', label: 'Tutor and blackboard' },
  { id: 'video', label: 'Manim video' },
  { id: 'quiz', label: 'Quizzes' },
  { id: 'trouble', label: 'Troubleshooting' },
];

const Documentation: React.FC = () => {
  const [open, setOpen] = useState('start');

  return (
    <div className="min-h-screen bg-[var(--sl-cream)] text-[#1e1b14]">
      <nav className="border-b border-[#debfc2] bg-white/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
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
            <Link to="/sdk" className="rounded-md px-2 py-1 text-[#3d3834] hover:bg-[#f5ebe0]">
              SDK
            </Link>
            <span className="px-2 py-1 text-xs text-[#8b1538]">Documentation</span>
          </div>
        </div>
      </nav>

      <div className="border-b border-[#4a0a1c]/10 bg-[#1a0a0f] py-10 text-[#fdf5e8]">
        <div className="mx-auto max-w-6xl px-4">
          <p className="sl-eyebrow text-[#b8a199]">// DOCS</p>
          <h1 className="mt-3 text-sm leading-relaxed md:text-base" style={{ fontFamily: 'var(--font-pixel)' }}>
            How routes map to the backend.
          </h1>
        </div>
      </div>

      <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 md:grid-cols-[14rem_1fr]">
        <aside className="space-y-1">
          {SECTIONS.map((s) => (
            <button
              key={s.id}
              type="button"
              onClick={() => setOpen(s.id)}
              className={
                'w-full rounded-md px-3 py-2 text-left text-sm ' +
                (open === s.id ? 'bg-[#8b1538] text-white' : 'bg-white text-[#1e1b14] ring-1 ring-[#debfc2] hover:bg-[#f5ebe0]')
              }
            >
              {s.label}
            </button>
          ))}
        </aside>
        <article className="rounded-xl border border-[#debfc2] bg-white p-6 text-sm text-[#4a433d]">
          {open === 'start' && (
            <div className="space-y-3">
              <h2 className="text-base font-semibold text-[#1e1b14]">Start</h2>
              <p>
                Run the API on port 8000, run Vite, and use the in-app <span className="font-mono">/api</span> proxy.
                Pick a grade on the home page or in settings so <span className="font-mono">grade_level</span> is set
                for all calls.
              </p>
              <p>
                <Link to="/app" className="font-medium text-[#8b1538] underline">
                  App hub
                </Link>
                {' lists the three product surfaces. '}
              </p>
            </div>
          )}
          {open === 'tutor' && (
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-base font-semibold text-[#1e1b14]">
                <IconChalkboard className="h-6 w-6 text-[#8b1538]" />
                Tutor
              </h2>
              <p>
                Route: <span className="font-mono">/tutor</span>. The UI posts to <span className="font-mono">POST
                /api/explain</span> with <span className="font-mono">question</span>,{' '}
                <span className="font-mono">student_id</span>, <span className="font-mono">grade_level</span>,{' '}
                <span className="font-mono">language</span>.
              </p>
              <p>Blackboard rendering is implemented on the tutor page, not in this document.</p>
            </div>
          )}
          {open === 'video' && (
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-base font-semibold text-[#1e1b14]">
                <IconFilm className="h-6 w-6 text-[#8b1538]" />
                Video (Manim)
              </h2>
              <p>
                Route: <span className="font-mono">/videos</span>. The UI calls <span className="font-mono">POST
                /api/generate-video</span> with a topic, student id, and grade. The backend is responsible for Manim
                render and serving files under the configured static path.
              </p>
            </div>
          )}
          {open === 'quiz' && (
            <div className="space-y-3">
              <h2 className="flex items-center gap-2 text-base font-semibold text-[#1e1b14]">
                <IconListCheck className="h-6 w-6 text-[#8b1538]" />
                Quiz
              </h2>
              <p>
                Route: <span className="font-mono">/quiz</span>. Uses <span className="font-mono">POST
                /api/quiz/generate</span> and <span className="font-mono">POST /api/quiz/submit</span> when the server
                exposes them. The student profile is updated on the server when the pipeline is enabled.
              </p>
            </div>
          )}
          {open === 'trouble' && (
            <div className="space-y-3">
              <h2 className="text-base font-semibold text-[#1e1b14]">Troubleshooting</h2>
              <p>
                If the app shows a connection error, confirm the backend is running, CORS and proxy are correct, and
                the fast <span className="font-mono">GET /api/ping</span> route responds.
              </p>
            </div>
          )}
        </article>
      </div>

      <div className="border-t border-[#debfc2] bg-[#f5ebe0] py-8 text-center text-sm text-[#5c534c]">
        <IconBook className="mx-auto mb-2 h-5 w-5 text-[#8b1538]" />
        <Link to="/" className="text-[#8b1538] underline">
          Return home
        </Link>
      </div>
    </div>
  );
};

export default Documentation;
