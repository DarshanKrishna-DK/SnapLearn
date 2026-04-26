"""
Narration text, TTS, and muxing spoken audio into Manim-produced MP4.
Uses edge-tts when available, else gTTS, then ffmpeg to mux.
"""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Rough words per minute for on-screen / spoken planning
SPOKEN_WPM = 130


def target_word_count(target_minutes: float) -> int:
    m = max(0.5, min(15.0, target_minutes))
    return int(m * SPOKEN_WPM)


async def generate_narration_text(
    gemini_client,
    model_name: str,
    topic: str,
    grade_level: str,
    language: str,
    target_minutes: float,
    extra_context: Optional[str] = None,
) -> str:
    """Single continuous narration for TTS, sized to target video length."""
    if not gemini_client:
        return f"Here is a short introduction to {topic} for grade {grade_level}."
    words = target_word_count(target_minutes)
    extra = f"\nAdditional context from the teacher or student:\n{extra_context}\n" if (extra_context or "").strip() else ""
    prompt = f"""Write a single continuous lesson narration script to be read aloud (text-to-speech) for students.
Topic: {topic}
Grade: {grade_level}
Language code: {language} (write the script entirely in this language)
Target spoken length: about {target_minutes:.1f} minutes, roughly {words} words.
Rules:
- Plain sentences only. No sound effects, no stage directions, no bullet lists.
- Short paragraphs separated by newlines. No emojis.
- Cover definitions, one worked example if relevant, and a short recap.
{extra}
Output only the narration text, no title line."""

    def _call():
        r = gemini_client.models.generate_content(model=model_name, contents=prompt)
        return (r.text or "").strip()

    try:
        text = await asyncio.to_thread(_call)
        if not text or len(text) < 50:
            return f"Let us learn about {topic}. This topic is important for grade {grade_level}."
        return text
    except Exception as e:
        logger.error("Narration generation failed: %s", e)
        return f"Let us explore {topic} together, step by step, at the right level for grade {grade_level}."


def _split_tts_chunks(text: str, max_len: int = 3200) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    n = 0
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p:
            continue
        if n + len(p) + 2 > max_len and buf:
            parts.append("\n\n".join(buf))
            buf = [p]
            n = len(p)
        else:
            buf.append(p)
            n += len(p) + 2
    if buf:
        parts.append("\n\n".join(buf))
    return parts if parts else [text[: max_len - 1]]


def _gtts_lang(code: str) -> str:
    c = (code or "en").lower().split("-")[0]
    m = {
        "en": "en",
        "hi": "hi",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "zh": "zh",
        "ja": "ja",
        "kn": "kn",
    }
    return m.get(c, "en")


async def _edge_tts_save(text: str, language: str, out_path: Path) -> bool:
    try:
        import edge_tts

        # Map simple codes to a voice; override with EDGE_TTS_VOICE in env
        import os

        custom = (os.environ.get("EDGE_TTS_VOICE") or "").strip()
        if custom:
            voice = custom
        else:
            lang = (language or "en").lower()
            if lang.startswith("hi"):
                voice = "hi-IN-SwaraNeural"
            elif lang.startswith("kn"):
                voice = "kn-IN-SapnaNeural"
            elif lang.startswith("es"):
                voice = "es-ES-ElviraNeural"
            else:
                voice = "en-US-AriaNeural"
        com = edge_tts.Communicate(text, voice)
        await com.save(str(out_path))
        return out_path.is_file() and out_path.stat().st_size > 0
    except Exception as e:
        logger.debug("edge-tts failed: %s", e)
        return False


def _gtts_save_sync(text: str, language: str, out_path: Path) -> bool:
    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang=_gtts_lang(language))
        tts.save(str(out_path))
        return out_path.is_file() and out_path.stat().st_size > 0
    except Exception as e:
        logger.warning("gTTS failed: %s", e)
        return False


async def _concat_audio_mp3(paths: list[Path], out: Path) -> bool:
    try:
        from pydub import AudioSegment

        merged = AudioSegment.empty()
        for p in paths:
            if p.suffix.lower() == ".mp3":
                merged += AudioSegment.from_mp3(str(p))
            elif p.suffix.lower() == ".wav":
                merged += AudioSegment.from_wav(str(p))
            else:
                merged += AudioSegment.from_file(str(p))
        merged.export(str(out), format="mp3")
        return out.is_file()
    except Exception as e:
        logger.error("pydub merge failed: %s", e)
        return False


async def synthesize_speech_to_file(
    text: str,
    language: str,
    out_mp3: Path,
) -> Tuple[bool, str]:
    """
    Returns (ok, engine_name).
    Tries edge-tts on full text; on failure chunks + gTTS, then merge.
    """
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    clean = re.sub(r"\s+", " ", (text or "").strip())
    if not clean:
        return False, "none"

    ok = await _edge_tts_save(clean, language, out_mp3)
    if ok:
        return True, "edge-tts"

    chunks = _split_tts_chunks(clean, 3000)
    if len(chunks) == 1:
        o = await asyncio.to_thread(_gtts_save_sync, chunks[0], language, out_mp3)
        return (o, "gtts" if o else "none")

    temp_dir = out_mp3.parent / f"_tts_parts_{out_mp3.stem}"
    temp_dir.mkdir(exist_ok=True)
    part_paths: list[Path] = []
    for i, ch in enumerate(chunks):
        p = temp_dir / f"part_{i:03d}.mp3"
        o = await asyncio.to_thread(_gtts_save_sync, ch, language, p)
        if o:
            part_paths.append(p)
    if not part_paths:
        return False, "none"
    if len(part_paths) == 1:
        shutil.copy2(part_paths[0], out_mp3)
        return True, "gtts"
    ok_m = await _concat_audio_mp3(part_paths, out_mp3)
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except OSError:
        pass
    return (ok_m, "gtts" if ok_m else "none")


def ffmpeg_invoked() -> bool:
    return shutil.which("ffmpeg") is not None


def mux_video_audio(
    video_mp4: Path,
    audio_mp3: Path,
    out_mp4: Path,
) -> bool:
    if not video_mp4.is_file() or not audio_mp3.is_file():
        return False
    if not ffmpeg_invoked():
        logger.error("ffmpeg not on PATH; cannot mux audio")
        return False
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    # Re-encode audio to AAC; copy video stream for speed; shortest stream sets duration
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_mp4),
        "-i",
        str(audio_mp3),
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-shortest",
        str(out_mp4),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        logger.error("ffmpeg mux failed: %s", (r.stderr or r.stdout)[: 2000])
        return False
    return out_mp4.is_file() and out_mp4.stat().st_size > 0
