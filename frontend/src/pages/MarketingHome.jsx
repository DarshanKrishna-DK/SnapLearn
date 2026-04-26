import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { IconChalkboard, IconFilm, IconListCheck, IconBook, IconX, IconTarget } from '../components/ui/SlIcons';

const GRADES = [
  { id: 'K', label: 'K' },
  ...[...Array(8)].map((_, i) => ({ id: String(i + 1), label: String(i + 1) })),
];

const MarketingHome = () => {
  const navigate = useNavigate();
  const [selectedGrade, setSelectedGrade] = useState(null);
  const [uiLang, setUiLang] = useState('en');

  useEffect(() => {
    const s = localStorage.getItem('selectedLanguage');
    if (s === 'en' || s === 'kn') {
      setUiLang(s);
    }
  }, []);

  const setLanguage = (code) => {
    setUiLang(code);
    localStorage.setItem('selectedLanguage', code);
  };

  const setGrade = (id) => {
    setSelectedGrade(id);
  };

  const continueWithGrade = () => {
    if (!selectedGrade) {
      return;
    }
    localStorage.setItem('selectedGrade', selectedGrade);
    localStorage.setItem('selectedLanguage', uiLang);
    navigate('/app');
  };

  const go = (to) => () => navigate(to);

  return (
    <div
      className="min-h-screen w-full"
      style={{
        backgroundColor: '#3d0a1c',
        color: '#f5e6d8',
        fontFamily: "var(--font-pixel), system-ui, sans-serif",
      }}
    >
      <header className="sl-pixel-panel mx-auto max-w-6xl border-x-0 border-t-0 p-0 sm:mx-4 sm:mt-3">
        <div
          className="flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4"
          style={{ background: 'linear-gradient(180deg, #2d060f 0%, #3d0a1c 100%)' }}
        >
          <Link
            to="/"
            className="text-[0.5rem] leading-tight text-[#fdf5e8] sm:text-[0.55rem]"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            SnapLearn
          </Link>
          <nav
            className="flex max-w-full flex-wrap items-center justify-end gap-2"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            <a
              href="#problem"
              className="sl-pixel-3d--outline sl-pixel-3d !py-2 !px-2.5 !text-[0.4rem] sm:!text-[0.5rem]"
            >
              PROBLEM
            </a>
            <a
              href="#product"
              className="sl-pixel-3d--outline sl-pixel-3d !py-2 !px-2.5 !text-[0.4rem] sm:!text-[0.5rem]"
            >
              MODES
            </a>
            <button
              type="button"
              onClick={go('/docs')}
              className="sl-pixel-3d--outline sl-pixel-3d !py-2 !px-2.5 !text-[0.4rem] sm:!text-[0.5rem]"
            >
              DOCS
            </button>
            <button
              type="button"
              onClick={go('/sdk')}
              className="sl-pixel-3d--outline sl-pixel-3d !py-2 !px-2.5 !text-[0.4rem] sm:!text-[0.5rem]"
            >
              SDK
            </button>
            <button type="button" onClick={go('/app')} className="sl-pixel-3d !py-2 !px-2.5 !text-[0.4rem] sm:!text-[0.5rem]">
              HUB
            </button>
          </nav>
        </div>
      </header>

      <section
        className="border-b-2 border-[#140308]"
        style={{ background: 'radial-gradient(120% 80% at 50% 0%, #5a1328 0%, #3d0a1c 45%, #2a050f 100%)' }}
      >
        <div className="mx-auto max-w-6xl px-4 py-14 md:py-20">
          <p
            className="mb-4 pl-0.5 text-left text-[0.35rem] uppercase leading-relaxed text-[#c49a5c] sm:mb-6 sm:text-[0.45rem]"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            // K-8 + KANNADA-ready // GEMINI-powered
          </p>
          <h1
            className="max-w-4xl text-left text-balance text-[0.72rem] leading-[1.55] sm:text-sm md:text-base"
            style={{ fontFamily: 'var(--font-pixel)', color: '#fff5eb' }}
          >
            Pixel-tutor, blackboard, and Manim video. Many teaching modes. English or Kannada script from Gemini.
          </h1>
          <p
            className="mt-5 max-w-2xl text-left text-[0.4rem] leading-[1.9] sm:text-xs md:text-sm"
            style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: '#e8d4c8' }}
          >
            Built for K through 8. Explanations adapt to your grade, language (including Kannada for narration and
            on-screen text when you pick it), and learning style. SnapLearn is not a single long lecture: you get tutor
            help, a generated clip, and a check-your-understanding step.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-2 sm:gap-3" style={{ fontFamily: 'var(--font-pixel)' }}>
            <button type="button" onClick={go('/tutor')} className="sl-pixel-3d !text-[0.48rem] sm:!text-[0.55rem]">
              TUTOR
            </button>
            <button type="button" onClick={go('/videos')} className="sl-pixel-3d--outline sl-pixel-3d !text-[0.48rem] sm:!text-[0.55rem]">
              VIDEO
            </button>
            <button
              type="button"
              onClick={go('/test')}
              className="sl-pixel-3d--outline sl-pixel-3d !text-[0.48rem] sm:!text-[0.55rem]"
            >
              PRACTICE TEST
            </button>
            <button
              type="button"
              onClick={go('/app')}
              className="!border-none !bg-transparent !p-0 !text-[0.4rem] !text-[#c49a5c] underline decoration-[#c49a5c] underline-offset-2 shadow-none"
              style={{ fontFamily: 'var(--font-pixel)' }}
            >
              HUB
            </button>
          </div>
        </div>
      </section>

      <section
        className="border-b-2 border-[#140308]"
        id="problem"
        style={{ background: 'linear-gradient(180deg, #2f0814 0%, #3d0a1c 100%)' }}
      >
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-12 md:grid-cols-2 md:items-center">
          <div>
            <p
              className="text-[0.4rem] uppercase sm:text-[0.45rem]"
              style={{ fontFamily: 'var(--font-mono)', color: '#b89a90' }}
            >
              // THE PROBLEM
            </p>
            <h2
              className="mt-3 text-[0.6rem] leading-[1.45] sm:text-xs"
              style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
            >
              One-size-fits-all explanations fail.
            </h2>
            <p className="mt-4 text-sm leading-relaxed" style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: '#e0ccc2' }}>
              If content ignores grade, language, and how you learn best, the blackboard and video cannot do their job.
              SnapLearn ties the API to a chosen grade, optional Kannada, and a stored learner profile.
            </p>
          </div>
          <ul
            className="sl-pixel-panel space-y-3 p-5 text-sm"
            style={{ fontFamily: "'IBM Plex Sans', sans-serif", color: '#e8d4c8' }}
          >
            <li className="flex gap-3">
              <span className="shrink-0 text-[#e07a8f]">
                <IconX className="h-5 w-5" />
              </span>
              <span>Text walls with no structure for a specific class band.</span>
            </li>
            <li className="flex gap-3">
              <span className="shrink-0 text-[#e07a8f]">
                <IconTarget className="h-5 w-5" />
              </span>
              <span>Videos that do not line up with what the tutor just explained.</span>
            </li>
            <li className="flex gap-3">
              <span className="shrink-0 text-[#e07a8f]">
                <IconListCheck className="h-5 w-5" />
              </span>
              <span>Quizzes that ignore the same profile the tutor and video use.</span>
            </li>
          </ul>
        </div>
      </section>

      <section
        className="border-b-2 border-[#140308]"
        id="product"
        style={{ background: 'linear-gradient(180deg, #3d0a1c 0%, #2a050f 100%)' }}
      >
        <div className="mx-auto max-w-6xl px-4 py-14">
          <p
            className="text-[0.4rem] uppercase sm:text-[0.45rem]"
            style={{ fontFamily: 'var(--font-mono)', color: '#b89a90' }}
          >
            // TEACHING TYPES
          </p>
          <h2
            className="mt-2 text-[0.58rem] leading-[1.45] sm:text-xs"
            style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
          >
            Visual, auditory, reading, and mixed. Same maroon home.
          </h2>
          <p
            className="mt-3 text-sm text-[#e0ccc2] md:max-w-2xl"
            style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}
          >
            The app stores a learning style when your profile and assessments feed it. Tutor prompts ask Gemini to lean
            into that mode when it makes sense: more diagrams for visual learners, calmer text for read-write, stepwise
            read-aloud for auditory. Kannada and English both flow through the same API with a language field.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <div className="sl-pixel-panel flex flex-col p-5">
              <span className="text-[#e8a0b0]">
                <IconChalkboard className="h-8 w-8" />
              </span>
              <h3
                className="mt-3 text-[0.5rem] leading-[1.5] sm:text-[0.55rem]"
                style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
              >
                TUTOR
              </h3>
              <p className="mt-2 text-sm text-[#d8c4b8]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
                Ask a question. Get an explanation and board-style script from Gemini.
              </p>
              <button type="button" onClick={go('/tutor')} className="sl-pixel-3d mt-4 w-fit !text-[0.45rem] sm:!text-[0.5rem]">
                OPEN
              </button>
            </div>
            <div className="sl-pixel-panel flex flex-col p-5">
              <span className="text-[#e8a0b0]">
                <IconFilm className="h-8 w-8" />
              </span>
              <h3
                className="mt-3 text-[0.5rem] leading-[1.5] sm:text-[0.55rem]"
                style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
              >
                MANIM
              </h3>
              <p className="mt-2 text-sm text-[#d8c4b8]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
                K-8 topic plus optional TTS. Pick Kannada so narration and on-screen text match your class.
              </p>
              <button type="button" onClick={go('/videos')} className="sl-pixel-3d mt-4 w-fit !text-[0.45rem] sm:!text-[0.5rem]">
                OPEN
              </button>
            </div>
            <div className="sl-pixel-panel flex flex-col p-5">
              <span className="text-[#e8a0b0]">
                <IconListCheck className="h-8 w-8" />
              </span>
              <h3
                className="mt-3 text-[0.5rem] leading-[1.5] sm:text-[0.55rem]"
                style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
              >
                PRACTICE TEST
              </h3>
              <p className="mt-2 text-sm text-[#d8c4b8]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
                Check understanding. Posts back to the student id you set in the app.
              </p>
              <button
                type="button"
                onClick={go('/test')}
                className="sl-pixel-3d mt-4 w-fit !text-[0.45rem] sm:!text-[0.5rem]"
              >
                OPEN
              </button>
            </div>
          </div>
        </div>
      </section>

      <section style={{ background: 'linear-gradient(180deg, #1f050c 0%, #3d0a1c 100%)' }}>
        <div className="mx-auto max-w-6xl px-4 py-12">
          <p
            className="text-[0.4rem] uppercase sm:text-[0.45rem]"
            style={{ fontFamily: 'var(--font-mono)', color: '#b89a90' }}
            id="grades"
          >
            // LANGUAGE (GEMINI) + K-8 GRADE
          </p>
          <h2
            className="mt-2 text-[0.55rem] leading-[1.5] sm:text-xs"
            style={{ fontFamily: 'var(--font-pixel)', color: '#fff0e5' }}
          >
            English or Kannada, then a grade. Stored for APIs.
          </h2>
          <p className="mt-3 text-sm text-[#e0ccc2]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
            Choosing Kannada (ಕನ್ನಡ) sets language to <code className="text-[#ffd4a0]">kn</code> for the tutor, quiz, and
            video + TTS. Gemini writes explanations and video narration in that language. Edge-tts and gTTS can speak
            Kannada when the backend is configured.
          </p>
          <div
            className="mt-4 flex flex-wrap items-center gap-2"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            <span className="text-[0.45rem] text-[#b89a90]">LANG:</span>
            <button
              type="button"
              onClick={() => setLanguage('en')}
              className={uiLang === 'en' ? 'sl-pixel-3d sl-pixel-3d--sm' : 'sl-pixel-3d--outline sl-pixel-3d sl-pixel-3d--sm'}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => setLanguage('kn')}
              className={uiLang === 'kn' ? 'sl-pixel-3d sl-pixel-3d--sm' : 'sl-pixel-3d--outline sl-pixel-3d sl-pixel-3d--sm'}
            >
              KN
            </button>
            <span className="pl-1 text-[0.35rem] sl-font-local text-[#deb899] sm:pl-2" style={{ fontFamily: 'var(--font-kn)' }}>
              (ಕನ್ನಡ)
            </span>
          </div>
          <div
            className="mt-4 flex max-w-3xl flex-wrap items-center gap-1.5 sm:gap-2"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            {GRADES.map((g) => (
              <button
                key={g.id}
                type="button"
                onClick={() => setGrade(g.id)}
                className={
                  selectedGrade === g.id
                    ? 'sl-pixel-3d sl-pixel-3d--sm !min-w-[2.1rem] border-[#ffd4a0]'
                    : 'sl-pixel-3d--outline sl-pixel-3d sl-pixel-3d--sm !min-w-[2.1rem]'
                }
              >
                {g.label}
              </button>
            ))}
          </div>
          {selectedGrade && (
            <p className="mt-3 text-sm text-[#c9b0a2]" style={{ fontFamily: "'IBM Plex Sans', sans-serif" }}>
              Grade {selectedGrade} and language {uiLang === 'kn' ? 'Kannada' : 'English'} will be sent as{' '}
              <code className="text-[#ffd4a0]">grade_level</code> and <code className="text-[#ffd4a0]">language</code>.
            </p>
          )}
          <div className="mt-5 flex flex-wrap items-center gap-2" style={{ fontFamily: 'var(--font-pixel)' }}>
            <button
              type="button"
              onClick={continueWithGrade}
              disabled={!selectedGrade}
              className="sl-pixel-3d !text-[0.48rem] sm:!text-[0.55rem]"
            >
              SAVE + HUB
            </button>
            <button
              type="button"
              onClick={go('/tutor')}
              className="sl-pixel-3d--outline sl-pixel-3d !text-[0.45rem] sm:!text-[0.5rem]"
            >
              SKIP: TUTOR
            </button>
            <button
              type="button"
              onClick={go('/test')}
              className="sl-pixel-3d--outline sl-pixel-3d !text-[0.45rem] sm:!text-[0.5rem]"
            >
              SKIP: TEST
            </button>
          </div>
        </div>
      </section>

      <section
        className="border-t-2 border-[#2a0a10]"
        style={{ background: 'radial-gradient(100% 100% at 50% 0%, #4a1520 0%, #2d060e 100%)' }}
      >
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-8 md:flex-row md:items-center md:justify-between">
          <div>
            <p
              className="text-[0.4rem] uppercase"
              style={{ fontFamily: 'var(--font-mono)', color: '#b8a199' }}
            >
              // DOCS + API
            </p>
            <h2
              className="mt-1 text-[0.5rem] leading-tight sm:text-xs"
              style={{ fontFamily: 'var(--font-pixel)', color: '#fdf5e8' }}
            >
              How endpoints work
            </h2>
          </div>
          <div className="flex flex-wrap gap-2" style={{ fontFamily: 'var(--font-pixel)' }}>
            <button
              type="button"
              onClick={go('/docs')}
              className="sl-pixel-3d--outline sl-pixel-3d !inline-flex !items-center !gap-2 !text-[0.42rem] sm:!text-[0.5rem]"
            >
              <IconBook className="h-3.5 w-3.5" style={{ minWidth: 14 }} />
              DOCS
            </button>
            <button
              type="button"
              onClick={go('/sdk')}
              className="sl-pixel-3d--outline sl-pixel-3d !text-[0.42rem] sm:!text-[0.5rem]"
            >
              SDK
            </button>
          </div>
        </div>
      </section>

      <footer
        className="border-t-2 border-[#140308] py-6 text-sm text-[#a09088]"
        style={{ background: '#1a0409', fontFamily: "'IBM Plex Sans', sans-serif" }}
      >
        <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 sm:flex-row sm:justify-between">
          <p> SnapLearn. K-8, Kannada-ready, Gemini-powered. </p>
          <div
            className="flex gap-3"
            style={{ fontFamily: 'var(--font-pixel)' }}
          >
            <Link to="/" className="text-[0.45rem] text-[#deb899] hover:text-[#fff]">
              HOME
            </Link>
            <Link to="/app" className="text-[0.45rem] text-[#deb899] hover:text-[#fff]">
              HUB
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MarketingHome;
