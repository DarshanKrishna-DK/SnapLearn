import { useEffect, useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { BoardScript } from '@/types';

const CHALK = '#e8e4a8';
const WOOD = '#2a1810';

type Props = {
  script: BoardScript;
  activeIndex: number;
  onIndexChange: (i: number) => void;
  autoPlayAll?: boolean;
};

function msPerCharForStep(
  text: string,
  drawDurationMs: number | undefined
): number {
  if (drawDurationMs && text.length > 0) {
    return Math.max(10, Math.min(100, drawDurationMs / text.length));
  }
  if (text.length < 200) {
    return 20;
  }
  return 12;
}

/**
 * Chalkboard with character-by-character reveal so the board reads like live writing.
 */
export function ChalkBlackboard({ script, activeIndex, onIndexChange, autoPlayAll = false }: Props) {
  const steps = script?.steps?.length ? script.steps : [];
  const step = steps[activeIndex];
  const text = step?.content ?? '';
  const [displayed, setDisplayed] = useState('');

  const onIndexChangeRef = useRef(onIndexChange);
  onIndexChangeRef.current = onIndexChange;

  const tickRef = useRef<number | null>(null);

  const clearTick = useCallback(() => {
    if (tickRef.current !== null) {
      window.clearInterval(tickRef.current);
      tickRef.current = null;
    }
  }, []);

  const [replay, setReplay] = useState(0);

  useEffect(() => {
    if (!text) {
      setDisplayed('');
      return;
    }
    let i = 0;
    setDisplayed('');
    const mspc = msPerCharForStep(text, step?.draw_duration_ms);
    clearTick();
    const id = window.setInterval(() => {
      i += 1;
      if (i > text.length) {
        clearTick();
        if (autoPlayAll && activeIndex < steps.length - 1) {
          window.setTimeout(() => onIndexChangeRef.current(activeIndex + 1), 1000);
        }
        return;
      }
      setDisplayed(text.slice(0, i));
    }, mspc);
    tickRef.current = id;
    return () => {
      clearTick();
    };
  }, [text, step, activeIndex, autoPlayAll, steps.length, clearTick, replay]);

  if (!steps.length) {
    return null;
  }

  return (
    <div className="w-full" style={{ perspective: '1200px' }}>
      <motion.div
        className="relative overflow-hidden rounded border-4 shadow-2xl"
        style={{
          background: 'radial-gradient(120% 100% at 50% 0%, #1a3d28 0%, #0d1f16 45%, #070d0a 100%)',
          borderColor: WOOD,
          minHeight: '14rem',
          boxShadow: '0 0 0 2px #1a1008, 0 18px 40px rgba(0,0,0,0.55), inset 0 0 80px rgba(0,0,0,0.35)',
        }}
        initial={{ rotateX: 0 }}
        whileInView={{ rotateX: 2 }}
        transition={{ type: 'spring', stiffness: 40 }}
        viewport={{ once: true }}
      >
        <div className="sl-scan pointer-events-none absolute inset-0 z-10 opacity-25" />
        <div
          className="pointer-events-none absolute -right-1 bottom-0 z-20 h-16 w-6 rotate-6 rounded"
          style={{
            background: 'linear-gradient(90deg, #c9c0b0 0%, #f0ebe0 40%, #8a7d70 100%)',
            boxShadow: '2px 2px 0 #3d3430',
          }}
          aria-hidden
        />
        <div className="relative z-0 p-4 pr-10 sm:p-6">
          <div
            className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-white/5 pb-2"
            style={{ color: 'rgba(255,255,255,0.35)' }}
          >
            <span className="font-mono text-[0.55rem] sm:text-xs">
              Step {activeIndex + 1} of {steps.length} — {step?.type ?? 'body'}
            </span>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="font-pixel text-[0.35rem] text-amber-200/90 underline-offset-2 hover:underline"
                onClick={() => {
                  clearTick();
                  setDisplayed(text);
                }}
              >
                SKIP
              </button>
              <button
                type="button"
                className="font-pixel text-[0.35rem] text-amber-200/90 underline-offset-2 hover:underline"
                onClick={() => {
                  setReplay((r) => r + 1);
                }}
              >
                REPLAY
              </button>
            </div>
          </div>
          <div
            className="min-h-[10rem] text-left text-base leading-relaxed sm:text-lg md:text-xl"
            style={{
              fontFamily: "'Caveat', cursive",
              color: CHALK,
              textShadow: '0 0 1px rgba(0,0,0,0.3), 1px 1px 0 rgba(0,0,0,0.15)',
            }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={activeIndex}
                initial={{ opacity: 0.9 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="whitespace-pre-wrap"
              >
                {displayed}
                <span
                  className="ml-0.5 inline-block w-1.5 animate-pulse rounded-sm bg-amber-100/90 align-middle"
                  style={{ height: '1.05em' }}
                />
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-1.5 border-t border-white/5 px-2 py-2.5 sm:px-3">
          {steps.map((s, i) => (
            <button
              key={`${s.step}-${i}`}
              type="button"
              onClick={() => onIndexChange(i)}
              className={`rounded border px-2.5 py-0.5 font-mono text-[0.5rem] transition ${
                i === activeIndex ? 'border-amber-300/80 bg-white/5 text-amber-200' : 'border-white/10 text-white/40'
              } focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300/60`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
