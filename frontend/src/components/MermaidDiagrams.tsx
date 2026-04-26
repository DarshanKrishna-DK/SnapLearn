import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';
import type { MermaidDiagram } from '@/types';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'strict',
  fontFamily: 'IBM Plex Mono, ui-monospace, monospace',
});

type Props = {
  diagrams: MermaidDiagram[];
};

/**
 * Renders Mermaid from API payloads below the chalkboard.
 */
export function MermaidDiagrams({ diagrams }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !diagrams.length) return;
    el.innerHTML = '';
    for (const d of diagrams) {
      const cap = document.createElement('p');
      cap.className = 'text-xs text-cream-200/60 font-body mb-1';
      cap.textContent = `${d.title} — ${d.description}`;
      el.appendChild(cap);
      const w = document.createElement('div');
      w.className = 'mermaid my-2 p-3 rounded-lg border border-cream-200/10 bg-black/30';
      w.textContent = d.mermaid_code;
      el.appendChild(w);
    }
    void mermaid.run({ nodes: el.querySelectorAll('.mermaid') });
  }, [diagrams]);

  if (!diagrams.length) return null;

  return (
    <div className="mt-6 sl-plate rounded-2xl p-5 sm:p-6">
      <h2 className="font-pixel text-[0.6rem] text-cream-100">DIAGRAMS</h2>
      <div ref={ref} className="mt-2 overflow-x-auto" />
    </div>
  );
}
