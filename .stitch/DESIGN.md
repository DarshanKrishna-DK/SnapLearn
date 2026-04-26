# SnapLearn UI (Stitch-aligned)

## Product

SnapLearn: FastAPI backend, K-8 alignment, optional Kannada, Gemini for explanations, Manim for video, adaptive quizzes. No placeholder metrics. Copy describes real system behavior.

## Reference structure (CyreneAI.com)

- Eyebrow lines with `//` and uppercase micro-labels.
- Hero: dominant headline, supporting line, two primary calls to action, secondary stats band (qualitative, not financial).
- Sections: full-viewport height bands, alternating structure (not repeated card grids).
- Footer: product name and resource links.

## Visual system (shady maroon, creamy white, pixel)

- **Backgrounds:** `maroon-950` to `maroon-700` gradients, soft vignettes.
- **Text:** `cream-100` to `cream-300`; **pixel font** (`font-pixel`, Press Start 2P) for headings, buttons, labels; **Space Grotesk** for long form body where pixel hurts readability; scale body with `text-sm` and generous line-height.
- **3D language:** `perspective` on parents, `transform rotateX/rotateY` on hover, multi-layer `box-shadow` (top highlight, bottom depth), beveled borders (`border` + inset shadow), optional `ring` gold tints.
- **Motion:** Framer Motion for scroll reveals, subtle float on key visuals, `whileHover` / `whileTap` on interactive 3D frames.
- **Icons:** Lucide icons inside beveled 3D frames, not flat-only.

## Layout rules

- **Minimum section height:** `min-h-[100dvh]`.
- **Responsiveness:** Stacked on narrow viewports, split columns from `md:` up, no overflow-x from fixed widths.
- **Accessibility:** `focus-visible:ring-2` on all buttons and links, semantic headings.

## Exclusions

- No emojis.
- No lorem or fake user counts, dollars, or test percentages.

---

_Generated to align with Stitch / taste agent expectations for a pixel, maroon-cream, Cyrene-structured marketing shell._
