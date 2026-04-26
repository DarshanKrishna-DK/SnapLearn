import { motion } from 'framer-motion';
import { PixelButton } from '@/components/PixelButton';
import { BookOpen, Zap, BarChart3, Code } from 'lucide-react';
import { IconFrame3D } from '@/components/IconFrame3D';
export function HomePage() {
  return (
    <main className="relative">
      <div className="pointer-events-none absolute inset-0 sl-scan z-0" />

      {/* Hero */}
      <section
        className="relative z-10 flex min-h-[100dvh] flex-col justify-center border-b border-cream-200/5 px-4 py-20"
        style={{
          background:
            'radial-gradient(120% 100% at 50% 0%, #8b2a54 0%, #3d1428 40%, #0f0206 100%)',
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-4 font-mono text-[0.5rem] uppercase tracking-[0.35em] text-gold-400/80"
        >
          // AI-POWERED ADAPTIVE LEARNING
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="max-w-4xl font-pixel text-[0.9rem] leading-tight text-cream-100 sm:text-xl md:text-2xl"
          style={{ textShadow: '0 3px 0 #080204' }}
        >
          SnapLearn: AI explanations, animated videos, and personalized quizzes for every level
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-6 max-w-2xl text-sm leading-relaxed text-cream-200/95 font-body sm:text-base"
        >
          Choose a topic, get instant explanations on an animated blackboard. Generate Manim videos with visual demonstrations of every concept. Take adaptive quizzes that adjust to your level. Your progress is saved in your student profile.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center"
        >
          <PixelButton to="/tutor" variant="solid" className="!min-w-[10rem]">
            START TUTORING
          </PixelButton>
          <PixelButton to="/quiz" variant="ghost">
            TAKE A QUIZ
          </PixelButton>
          <PixelButton to="/video" variant="ghost">
            WATCH VIDEO
          </PixelButton>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-10 max-w-xl text-[0.5rem] font-mono uppercase tracking-wide text-cream-300/60"
        >
          Built for real classrooms. Set language and level in your profile. Your student ID syncs progress across all tools.
        </motion.p>
      </section>

      {/* Core Features */}
      <section
        className="relative z-10 border-b border-cream-200/5 bg-gradient-to-b from-maroon-900/30 to-maroon-950/20 px-4 py-24"
        style={{ clipPath: 'polygon(0 0, 100% 2%, 100% 100%, 0 98%)' }}
      >
        <div className="mx-auto w-full max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-10%' }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="font-mono text-[0.5rem] uppercase text-gold-400/80">// THREE LEARNING PATHS</h2>
            <p className="mt-2 max-w-2xl text-sm text-cream-200/90 font-body">
              Each tool reinforces the others. Ask questions, watch videos, test yourself, and repeat.
            </p>
          </motion.div>

          <div className="mt-14 grid gap-6 sm:grid-cols-3">
            {[
              {
                icon: BookOpen,
                title: 'Tutor',
                body: 'Type any topic. Get an instant explanation tailored to your profile. Step-by-step chalk drawing shows how to work through it.',
                step: '01',
              },
              {
                icon: Zap,
                title: 'Video',
                body: 'The server renders animated lessons using Manim. Visual demonstrations, worked examples, and transformations. Not captions—actual drawings.',
                step: '02',
              },
              {
                icon: BarChart3,
                title: 'Quiz',
                body: 'Type a topic, generate questions from our bank. Your answers are graded server-side. Weak areas are saved to your profile for targeted review.',
                step: '03',
              },
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                className="sl-plate flex min-h-[14rem] flex-col rounded-2xl p-6 sm:p-7"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-8%' }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
              >
                <div className="mb-4 flex items-start justify-between">
                  <span className="font-pixel text-[0.5rem] text-gold-500/70">{feature.step}</span>
                  <IconFrame3D icon={feature.icon} label={feature.title} />
                </div>
                <h3 className="font-pixel text-[0.65rem] text-cream-100">{feature.title}</h3>
                <p className="mt-3 grow text-sm font-body leading-relaxed text-cream-200/90">{feature.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="relative z-10 border-b border-cream-200/5 px-4 py-24">
        <div className="mx-auto w-full max-w-6xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: '-10%' }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="font-mono text-[0.5rem] uppercase text-gold-400/80">// HOW IT WORKS</h2>
          </motion.div>

          <div className="mt-12 space-y-10">
            {[
              {
                num: '1',
                title: 'Set your profile',
                desc: 'Choose language and level in Profile. Explanations, video scripts, and quiz content follow those settings when supported.',
              },
              {
                num: '2',
                title: 'Create a Student ID',
                desc: 'Your student ID is the key. Every explanation, quiz result, and video watch time is logged to the same profile so we learn your strengths and gaps.',
              },
              {
                num: '3',
                title: 'Ask, Watch, Quiz, Repeat',
                desc: 'Use Tutor to learn a concept. Generate a Video to see it in action. Take a Quiz to test yourself. Your results shape what comes next.',
              },
              {
                num: '4',
                title: 'Your Profile Grows',
                desc: 'Over time, the system knows your learning style, weak topics, and current difficulty level. Quizzes become more targeted. Explanations adjust to your needs.',
              },
            ].map((item, i) => (
              <motion.div
                key={item.num}
                className="grid gap-6 md:grid-cols-12 md:items-start"
                initial={{ opacity: 0, x: -16 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-5%' }}
                transition={{ delay: i * 0.1, duration: 0.4 }}
              >
                <div className="md:col-span-2 flex items-start gap-3">
                  <span className="font-pixel text-[0.6rem] text-gold-400/80">{item.num}</span>
                </div>
                <div className="md:col-span-10">
                  <h3 className="font-pixel text-[0.6rem] text-cream-100">{item.title}</h3>
                  <p className="mt-2 text-sm font-body leading-relaxed text-cream-200/85">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Local API */}
      <section className="relative z-10 border-b border-cream-200/5 bg-gradient-to-b from-maroon-900/20 to-[#0f0206] px-4 py-24">
        <div className="mx-auto w-full max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-10%' }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="font-mono text-[0.5rem] uppercase text-gold-400/80">// RUN THE STACK</h2>
            <p className="mt-3 max-w-2xl text-sm text-cream-200/90 font-body">
              Use Profile to set student id, language, and level. Those values flow to Tutor, Video, and Quiz.
            </p>
          </motion.div>

          <div className="mt-10 max-w-3xl">
            <motion.div
              className="sl-plate rounded-2xl p-7 sm:p-8"
              initial={{ opacity: 0, scale: 0.96 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: '-5%' }}
              transition={{ duration: 0.4 }}
              style={{ transform: 'rotate(-0.2deg)' }}
            >
              <h3 className="font-pixel text-[0.6rem] text-cream-100">BACKEND SETUP</h3>
              <p className="mt-3 text-sm font-body leading-relaxed text-cream-200/85">
                The backend is a FastAPI service running on <code className="text-[0.85em] text-gold-400">localhost:8000</code>. It connects to Google Gemini for explanations, Manim for video rendering, and stores your student profiles locally.
              </p>
              <p className="mt-3 text-sm font-body leading-relaxed text-cream-200/85">
                To enable videos, install backend dependencies into the same Python environment that runs the API:
              </p>
              <code className="mt-2 block rounded bg-maroon-900/50 p-2 text-[0.7rem] text-cream-300/90 font-mono">
                pip install -r requirements.txt
              </code>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-block font-mono text-[0.5rem] text-gold-400/90 underline decoration-gold-400/40 decoration-1 underline-offset-3 transition hover:text-cream-100"
              >
                View API Docs &rarr;
              </a>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="relative z-10 border-b border-cream-200/5 px-4 py-24">
        <div className="mx-auto w-full max-w-6xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-10%' }}
            transition={{ duration: 0.4 }}
          >
            <h2 className="font-mono text-[0.5rem] uppercase text-gold-400/80">// TECHNOLOGY</h2>
            <p className="mt-3 max-w-2xl text-sm text-cream-200/90 font-body">
              Built with modern, open-source tools. Everything runs locally by default.
            </p>
          </motion.div>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {[
              {
                icon: Code,
                label: 'Frontend',
                desc: 'React + Vite, Tailwind CSS, Framer Motion. Pixel-themed UI for learners and instructors.',
              },
              {
                icon: Zap,
                label: 'Backend',
                desc: 'FastAPI with Python. Gemini for AI explanations. Manim for animated video generation.',
              },
              {
                icon: BarChart3,
                label: 'Data',
                desc: 'Student profiles stored locally as JSON. Quiz results and learning sessions tracked per student.',
              },
            ].map((tech, i) => (
              <motion.div
                key={tech.label}
                className="sl-plate rounded-lg p-5"
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-5%' }}
                transition={{ delay: i * 0.08, duration: 0.4 }}
              >
                <IconFrame3D icon={tech.icon} label={tech.label} />
                <h3 className="mt-3 font-pixel text-[0.55rem] text-cream-100">{tech.label}</h3>
                <p className="mt-2 text-xs font-body text-cream-200/85">{tech.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <section className="relative z-10 border-t border-cream-200/5 px-4 py-12 text-center">
        <p className="font-pixel text-[0.5rem] uppercase tracking-wide text-cream-300/60">
          SnapLearn. Adaptive learning. Real features. No fake metrics.
        </p>
      </section>
    </main>
  );
}
