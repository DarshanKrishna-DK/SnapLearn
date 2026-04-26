import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '../utils/api';
import { IconChalkboard, IconFilm, IconListCheck } from '../components/ui/SlIcons';

interface Props {
  studentId: string;
  gradeLevel: string;
  language: string;
}

const AppPage: React.FC<Props> = ({ studentId, gradeLevel }) => {
  const [profileError, setProfileError] = useState<string | null>(null);
  const [hasProfile, setHasProfile] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await apiClient.getStudentProfile(studentId);
        if (!cancelled) {
          setHasProfile(true);
          setProfileError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setHasProfile(false);
          setProfileError('Profile API unavailable. You can still use tutor, video, and quiz when the server is up.');
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [studentId]);

  return (
    <div className="min-h-screen bg-[var(--sl-cream)] text-[#1e1b14]">
      <header className="border-b border-[#debfc2] bg-white/80">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <Link
            to="/"
            className="text-xs font-bold uppercase tracking-wide text-[#8b1538]"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            SnapLearn
          </Link>
          <p className="text-sm text-[#5c534c]">
            Student: <span className="font-mono text-[#1e1b14]">{studentId}</span>
            {' · '}
            Grade: <span className="font-mono text-[#1e1b14]">{gradeLevel}</span>
          </p>
        </div>
      </header>

      <div className="mx-auto max-w-5xl px-4 py-10">
        <p className="sl-eyebrow text-[#8b1538]">// APP HUB</p>
        <h1 className="mt-2 text-sm leading-relaxed text-[#1e1b14] md:text-base" style={{ fontFamily: 'var(--font-pixel)' }}>
          Choose where to work. Each feature has its own page in this build.
        </h1>
        <p className="mt-4 max-w-2xl text-sm text-[#4a433d]">
          <strong>Blackboard and explanations</strong> are on the tutor page. <strong>Manim output</strong> (video
          generation) is on the video page. The quiz is on the quiz page. This hub does not duplicate those flows, so
          you always land in the right tool.
        </p>
        {profileError && <p className="mt-4 text-sm text-[#6d0f2b]">{profileError}</p>}
        {hasProfile && <p className="mt-4 text-sm text-[#5c534c]">Student profile loaded from the API.</p>}

        <ul className="mt-10 grid gap-4 md:grid-cols-3">
          <li>
            <Link
              to="/tutor"
              className="flex h-full flex-col rounded-xl border-2 border-[#debfc2] bg-white p-6 transition hover:border-[#8b1538]"
            >
              <span className="text-[#8b1538]">
                <IconChalkboard className="h-8 w-8" />
              </span>
              <span className="mt-3 text-sm font-semibold" style={{ fontFamily: 'var(--font-pixel)' }}>
                AI tutor
              </span>
              <span className="mt-2 text-sm text-[#5c534c]">Animated blackboard and structured explanations.</span>
            </Link>
          </li>
          <li>
            <Link
              to="/videos"
              className="flex h-full flex-col rounded-xl border-2 border-[#debfc2] bg-white p-6 transition hover:border-[#8b1538]"
            >
              <span className="text-[#8b1538]">
                <IconFilm className="h-8 w-8" />
              </span>
              <span className="mt-3 text-sm font-semibold" style={{ fontFamily: 'var(--font-pixel)' }}>
                Manim video
              </span>
              <span className="mt-2 text-sm text-[#5c534c]">Generate and view lesson video from a topic and grade.</span>
            </Link>
          </li>
          <li>
            <Link
              to="/quiz"
              className="flex h-full flex-col rounded-xl border-2 border-[#debfc2] bg-white p-6 transition hover:border-[#8b1538]"
            >
              <span className="text-[#8b1538]">
                <IconListCheck className="h-8 w-8" />
              </span>
              <span className="mt-3 text-sm font-semibold" style={{ fontFamily: 'var(--font-pixel)' }}>
                Quiz
              </span>
              <span className="mt-2 text-sm text-[#5c534c]">Submit answers; profile updates on the server when configured.</span>
            </Link>
          </li>
        </ul>

        <p className="mt-10 text-sm text-[#5c534c]">
          <Link to="/docs" className="font-medium text-[#8b1538] underline">
            Documentation
          </Link>
          {' · '}
          <Link to="/sdk" className="font-medium text-[#8b1538] underline">
            SDK
          </Link>
          {' · '}
          <Link to="/" className="font-medium text-[#8b1538] underline">
            Home
          </Link>
        </p>
      </div>
    </div>
  );
};

export default AppPage;
