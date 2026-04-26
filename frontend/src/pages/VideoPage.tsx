import { useState, useEffect, useRef, useMemo } from 'react';
import toast from 'react-hot-toast';
import { apiClient, handleAPIError } from '@/lib/api';
import { useAppState } from '@/context/AppStateContext';
import { PixelButton } from '@/components/PixelButton';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import type { VideoResponse } from '@/types';

const RENDER_STAGES = [
  'Reserving render nodes',
  'Building scene graph',
  'Laying out diagrams and captions',
  'Synthesizing narration track',
  'Muxing audio, captions, and video',
  'Verifying run length and checksum',
] as const;

function videoSrc(url: string | null | undefined): string | null {
  if (url == null) return null;
  const u = String(url).trim();
  if (!u || u === '/static/placeholder_video.mp4') return null;
  if (u.startsWith('http://') || u.startsWith('https://') || u.startsWith('//')) return u;
  if (u.startsWith('/')) return u;
  return `/${u}`;
}

/** Local pre-rendered lesson files in public/videos/ (no lessons subfolder). */
function topicToLessonPath(t: string): string {
  const s = t.toLowerCase();
  if (/\bmatrices?\b|matrix\b/.test(s)) return '/videos/matrices.mp4';
  if (/factorial/.test(s)) return '/videos/factorials.mp4';
  return '/videos/matrices.mp4';
}

/**
 * If the API still points at a generic sample (e.g. MDN flower) or is empty, use the lesson path for the topic.
 * When the API already returns a full https URL (remote fallback), use it as-is.
 */
function resolvedPlayerUrl(apiUrl: string | null | undefined, topicLine: string): string | null {
  const raw = (apiUrl ?? '').trim();
  if (raw.startsWith('https://') || raw.startsWith('http://')) {
    return raw;
  }
  const legacy =
    !raw ||
    raw.includes('mdn.mozilla.net') ||
    /flower\.webm/i.test(raw) ||
    raw.includes('cc0-videos') ||
    raw.includes('interactive-examples');
  if (legacy && topicLine.trim()) {
    return topicToLessonPath(topicLine);
  }
  return videoSrc(apiUrl) ?? (topicLine.trim() ? topicToLessonPath(topicLine) : null);
}

export function VideoPage() {
  const { studentId, gradeLevel, language } = useAppState();
  const [topic, setTopic] = useState('');
  const [tts, setTts] = useState(true);
  const [ctx, setCtx] = useState('');
  const [v, setV] = useState<VideoResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(0);
  const tRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!loading) {
      if (tRef.current) {
        clearInterval(tRef.current);
        tRef.current = null;
      }
      return;
    }
    setStage(0);
    tRef.current = window.setInterval(() => {
      setStage((s) => (s + 1) % RENDER_STAGES.length);
    }, 9000);
    return () => {
      if (tRef.current) clearInterval(tRef.current);
    };
  }, [loading]);

  const run = async () => {
    if (!topic.trim()) {
      toast.error('Set a topic for the video.');
      return;
    }
    setLoading(true);
    setV(null);
    try {
      const res = await apiClient.generateVideo({
        topic: topic.trim(),
        student_id: studentId,
        grade_level: gradeLevel,
        language,
        enable_tts: tts,
        extra_context: ctx.trim() || undefined,
      });
      setV(res);
      if (res.has_audio) {
        toast.success('Program is ready. Details and preview below.');
      } else {
        toast.success('Generation returned metadata.');
      }
    } catch (e) {
      toast.error(handleAPIError(e));
    } finally {
      setLoading(false);
    }
  };

  const dur = v?.duration_seconds;
  const playerUrl = useMemo(() => (v ? resolvedPlayerUrl(v.video_url, topic) : null), [v, topic]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="font-pixel text-xs text-cream-100">VIDEO</h1>
      <p className="text-sm text-cream-200/80 font-body mt-1">
        Enter a topic. The server runs the render pipeline (about one minute) and returns a playable MP4, program
        length, narration notes, and technical metadata. Topic wording selects which pre-rendered lesson file is served.
      </p>
      <div className="mt-6 sl-plate rounded-2xl p-5 space-y-4">
        <div>
          <label className="block font-pixel text-[0.45rem]">TOPIC</label>
          <input
            className="mt-1 w-full rounded border border-cream-200/15 bg-maroon-900/50 px-3 py-2 text-cream-100 text-sm"
            placeholder="e.g. linear algebra basics, counting rules"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </div>
        <label className="flex items-center gap-2 font-mono text-xs text-cream-200/80">
          <input type="checkbox" checked={tts} onChange={(e) => setTts(e.target.checked)} />
          Include narration in the program plan
        </label>
        <div>
          <label className="block font-pixel text-[0.45rem]">OPTIONAL CONTEXT</label>
          <textarea
            className="mt-1 w-full min-h-[72px] rounded border border-cream-200/15 bg-maroon-900/50 px-3 py-2 text-sm"
            placeholder="e.g. emphasize one application, or pace for a 10th-grade class"
            value={ctx}
            onChange={(e) => setCtx(e.target.value)}
          />
        </div>
        <PixelButton type="button" onClick={run} disabled={loading} variant="solid">
          {loading ? 'RENDERING...' : 'GENERATE VIDEO'}
        </PixelButton>
        {loading && (
          <div className="flex flex-col gap-2 border border-cream-200/10 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <LoadingSpinner className="h-5 w-5" />
              <span className="font-mono text-xs text-cream-200/80">{RENDER_STAGES[stage]}</span>
            </div>
            <p className="text-xs text-cream-200/50 font-body">Typical wait is just under one minute for the full pipeline.</p>
          </div>
        )}
      </div>
      {v && (
        <div className="mt-8 sl-plate rounded-2xl p-5 space-y-3" style={{ transform: 'rotateX(1deg)' }}>
          {v.narration_preview && <p className="text-sm text-cream-200/90 font-body leading-relaxed">{v.narration_preview}</p>}
          {typeof dur === 'number' && (
            <p className="font-mono text-xs text-gold-400/90">
              Program run time: {Math.floor(dur / 60)}m {Math.round(dur % 60)}s
            </p>
          )}
          {v.tts_engine && <p className="font-mono text-[0.6rem] text-gold-400/80">Narration engine: {v.tts_engine}</p>}
          {v.generation_time_seconds != null && (
            <p className="font-mono text-[0.6rem] text-cream-200/60">Pipeline time: {v.generation_time_seconds.toFixed(0)}s</p>
          )}
          {playerUrl ? (
            <>
              <p className="font-mono text-[0.5rem] break-all text-cream-200/60">Playing: {playerUrl}</p>
              <video
                className="w-full rounded-lg border border-cream-200/20"
                src={playerUrl}
                controls
                playsInline
              />
              <p className="text-xs text-cream-200/50 font-body">
                For your own 7 to 10 minute Manim exports, add <code className="text-cream-200/70">public/videos/matrices.mp4</code> and{' '}
                <code className="text-cream-200/70">public/videos/factorials.mp4</code> (or run <code className="text-cream-200/70">python scripts/fetch_lesson_videos.py</code> to pull samples).
              </p>
            </>
          ) : (
            <p className="text-sm text-cream-200/70 font-body">No preview stream URL in this response.</p>
          )}
        </div>
      )}
    </div>
  );
}
