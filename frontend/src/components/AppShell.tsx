import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Clapperboard, FileCode, Home, LayoutGrid, ListChecks, User } from 'lucide-react';
import { IconFrame3D } from './IconFrame3D';

const nav: { to: string; label: string; icon: typeof Home }[] = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/hub', label: 'Hub', icon: LayoutGrid },
  { to: '/tutor', label: 'Tutor', icon: BookOpen },
  { to: '/video', label: 'Video', icon: Clapperboard },
  { to: '/quiz', label: 'Quiz', icon: ListChecks },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/sdk', label: 'API', icon: FileCode },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const loc = useLocation();
  return (
    <div className="min-h-screen flex flex-col">
      <motion.header
        initial={false}
        className="sticky top-0 z-50 border-b border-cream-200/10 bg-maroon-950/95 backdrop-blur-md"
        style={{ boxShadow: '0 4px 0 #080204' }}
      >
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <Link
            to="/"
            className="group flex w-fit items-center gap-2 font-pixel text-[0.55rem] text-cream-100 sm:text-[0.62rem] focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400/70"
          >
            <div className="sl-icon-cube !p-2" style={{ boxShadow: '0 3px 0 #080204' }}>
              <span className="text-gold-400" aria-hidden>
                S
              </span>
            </div>
            <span>SNAPLEARN</span>
          </Link>
          <nav
            className="flex max-w-full flex-nowrap items-center justify-start gap-2 overflow-x-auto pb-0.5 sm:justify-end sm:pb-0"
            aria-label="Primary"
          >
            {nav.map(({ to, label, icon: I }) => {
              const active = loc.pathname === to || (to === '/quiz' && loc.pathname === '/test');
              return (
                <Link
                  key={to}
                  to={to}
                  className={`shrink-0 group flex items-center gap-1.5 rounded border border-transparent px-1.5 py-1.5 text-[0.4rem] font-pixel focus:outline-none focus-visible:ring-2 focus-visible:ring-gold-400/60 sm:px-2.5 ${
                    active
                      ? 'border-gold-400/30 bg-maroon-800/60 text-gold-400'
                      : 'text-cream-200/80 hover:border-cream-200/20 hover:text-cream-100'
                  }`}
                >
                  <IconFrame3D icon={I} label={label} className="!p-1.5" />
                  <span>{label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </motion.header>
      <div className="flex-1">{children}</div>
    </div>
  );
}
