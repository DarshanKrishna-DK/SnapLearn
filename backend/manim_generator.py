"""
Manim Video Generator for SnapLearn AI
Generates educational videos using Manim locally as subprocess; scripts from Gemini API
"""

import os
import logging
import subprocess
import json
import tempfile
import asyncio
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from models import VideoResponse, StudentProfile
from utils import schedule_async_init
from llm_service import get_llm_service
from video_narration import (
    generate_narration_text,
    synthesize_speech_to_file,
    mux_video_audio,
    ffmpeg_invoked,
)

logger = logging.getLogger(__name__)

class ManimGenerator:
    """Generates educational videos using Manim; LLM script generation uses Gemini only."""
    
    def __init__(self):
        _root = Path(__file__).resolve().parent.parent
        self.videos_dir = _root / "videos"
        self.temp_dir = _root / "temp_manim"
        self.prompts_dir = _root / "prompts"
        
        # Create directories
        self.videos_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # LLM: Gemini API only (GOOGLE_API_KEY or GEMINI_API_KEY in .env)
        self.llm = get_llm_service()
        
        # Production-grade target duration: minimum 2 minutes, no maximum for comprehensive learning
        self._target_minutes = max(2.0, float(os.getenv("MANIM_TARGET_MINUTES", "4.0")))

        # Create manim scene prompt template
        self._create_manim_prompt_template()
        
        logger.info("Manim generator initialized (LLM: Gemini API)")

    @staticmethod
    def _is_bad_manim_text(s: str) -> bool:
        t = (s or "").lower().strip()
        if not t:
            return True
        if "error generating" in t:
            return True
        if "def construct" not in t:
            return True
        if ("from manim" not in t) and ("import manim" not in t) and ("manim import" not in t):
            return True
        return False

    @staticmethod
    def _manim_has_import(s: str) -> bool:
        s = s or ""
        return ("from manim" in s) or ("import manim" in s) or ("from manim.utils" in s)
    
    def _create_manim_prompt_template(self):
        """Create the Manim scene generation prompt - long, teachable runtimes in minutes"""
        # target_minutes placeholder filled per request
        prompt_template = """You are a production-grade Manim Community (v0.18+) expert creating comprehensive educational videos. Generate ONE complete Python file for professional-quality video content. No markdown, no backticks, only executable Python code.

PRODUCTION REQUIREMENTS:
TARGET VIDEO LENGTH: {target_minutes} minutes minimum (NO MAXIMUM). This is a professional educational video that must provide thorough, comprehensive coverage.
TIMING CALCULATION: Plan for 60+ seconds of combined self.wait(...) calls per minute PLUS animation time. For {target_minutes} minutes, use AT LEAST {wait_time_minimum} seconds total in self.wait() calls.

STUDENT CONTEXT:
- Grade Level: {grade_level}  
- Topic: {topic}
- Language: {language}
- Learning Profile: {student_profile_summary}
- Audio Narration: This video will have professional narration and captions

MANDATORY PRODUCTION STANDARDS:
1) Import: from manim import *
2) Class: class ExplanationScene(Scene):
3) Method: def construct(self):
4) COMPREHENSIVE STRUCTURE: Create 8-12 major segments with clear progression:
   - Engaging title sequence (20+ seconds)
   - Concept introduction with context (40+ seconds)
   - Multiple worked examples (60+ seconds each)  
   - Visual breakdowns and step-by-step analysis (60+ seconds)
   - Common misconceptions and clarifications (40+ seconds)
   - Practice scenarios and applications (60+ seconds)
   - Comprehensive summary and key takeaways (30+ seconds)
   - Preview of next learning steps (20+ seconds)

5) VISUAL EXCELLENCE: Rich animations with varied objects:
   - Text, MathTex, geometric shapes, arrows, diagrams
   - Color palette: BLUE, YELLOW, GREEN, RED, ORANGE, WHITE, MAROON, TEAL, PURPLE
   - Transform, FadeIn, FadeOut, Write, Create, DrawBoundingRectangle
   - Group related content with VGroup for smooth transitions

6) PACING FOR LEARNING: Strategic wait times for comprehension:
   - Title screens: self.wait(8-12)
   - Complex concepts: self.wait(10-15) 
   - After equations: self.wait(6-10)
   - Between examples: self.wait(5-8)
   - Final summary: self.wait(12-20)

7) AUDIO-READY DESIGN: Content structured for narration:
   - Clear visual hierarchy matching audio flow
   - Highlight key terms that will be emphasized in narration
   - Pause points aligned with natural speech patterns

8) EDUCATIONAL DEPTH: 
   - Multiple approaches to the same concept
   - Real-world connections and applications  
   - Building complexity progressively
   - Clear connections between ideas

NARRATION CONTEXT (design visuals to support this audio):
{narration_excerpt}

ADDITIONAL CONTEXT:
{extra_context}

OUTPUT: Complete Python source code only. Create a video worthy of professional educational standards that provides comprehensive learning value for {target_minutes}+ minutes."""
        
        # Save the prompt template
        prompt_file = self.prompts_dir / "manim_scene.txt"
        prompt_file.parent.mkdir(exist_ok=True)
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_template)
        
        self.manim_prompt_template = prompt_template
    
    @staticmethod
    def _section_count_for_duration(target_minutes: float = 3.0) -> int:
        return 4

    async def generate_video(
        self,
        topic: str,
        grade_level: str,
        student_profile: StudentProfile,
        language: str = "en",
        enable_tts: bool = True,
        extra_context: Optional[str] = None,
    ) -> VideoResponse:
        """Generate educational video with RICH visual demonstrations (no user duration input)."""
        try:
            if not self.is_healthy():
                return self._create_fallback_video_response(
                    topic,
                    "Manim is not available in this Python environment. "
                    f"Install project deps with: \"{sys.executable}\" -m pip install -r requirements.txt "
                    "from the repository backend folder (or pip install manim in the same venv that runs the API).",
                )
            logger.info("Starting video generation for topic: %s (production visual mode, tts=%s)", topic, enable_tts)

            narration_text = ""
            gem = getattr(self.llm, "gemini_client", None) if self.llm else None
            model = getattr(self.llm, "gemini_model", "gemini-2.0-flash") if self.llm else "gemini-2.0-flash"
            if enable_tts and gem:
                narration_text = await generate_narration_text(
                    gem,
                    model,
                    topic,
                    str(grade_level),
                    language,
                    3.0,
                    extra_context=extra_context,
                )
            if (narration_text or "").strip():
                excerpt = (narration_text[:800] + "…") if len(narration_text) > 800 else narration_text
            else:
                excerpt = f"Visual demonstration lesson on {topic} for grade {grade_level}. Show multiple examples with animations and step-by-step transformations."
            manim_script = await self._generate_manim_script(
                topic,
                grade_level,
                student_profile,
                language,
                extra_context=extra_context,
                narration_excerpt=excerpt,
            )

            if not manim_script:
                raise Exception("Failed to generate Manim script")

            if not self._validate_manim_script(manim_script):
                manim_script = await self._fix_manim_script(manim_script, topic)

            video_info = await self._render_manim_video(manim_script, topic, self._target_minutes)
            lp = video_info.pop("local_video_path", None)
            vpath = Path(lp) if isinstance(lp, str) else (lp if isinstance(lp, Path) else None)

            has_audio = False
            tts_engine = None
            if (
                enable_tts
                and narration_text
                and vpath
                and vpath.is_file()
                and ffmpeg_invoked()
            ):
                audio_path = vpath.parent / f"{vpath.stem}_narration.mp3"
                out_path = vpath.parent / f"{vpath.stem}_with_audio.mp4"
                t_ok, tts_engine = await synthesize_speech_to_file(narration_text, language, audio_path)
                if t_ok and mux_video_audio(vpath, audio_path, out_path):
                    has_audio = True
                    try:
                        if vpath.is_file():
                            vpath.unlink()
                    except OSError:
                        pass
                    try:
                        if audio_path.is_file():
                            audio_path.unlink()
                    except OSError:
                        pass
                    video_name = out_path.name
                    video_info["video_url"] = f"/videos/{video_name}"
                    if video_info.get("duration_seconds") is None or video_info.get("duration_seconds", 0) < 0.1:
                        video_info["duration_seconds"] = await self._get_video_duration(out_path)
                    if video_info.get("file_size_mb") is not None and out_path.is_file():
                        video_info["file_size_mb"] = round(out_path.stat().st_size / (1024 * 1024), 2)
            elif enable_tts and not ffmpeg_invoked():
                logger.warning("TTS enabled but ffmpeg missing; video stays silent")
            elif enable_tts and not narration_text:
                logger.warning("TTS enabled but no narration text produced")

            video_info["has_audio"] = has_audio
            video_info["tts_engine"] = tts_engine
            video_info["narration_preview"] = (narration_text[:500] + "…") if len(narration_text) > 500 else (narration_text or None)

            return VideoResponse(**video_info)
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return self._create_fallback_video_response(topic, str(e))
    
    def _ls_style(self, student_profile: StudentProfile) -> str:
        ls = getattr(student_profile, "learning_style", None)
        if ls is None:
            return "mixed"
        v = getattr(ls, "value", None)
        return v if v is not None else str(ls)

    def _create_long_lesson_script(self, topic: str, grade_level: str) -> str:
        """Heuristic multi-minute scene when the LLM fails. Topic must be short for a Python string."""
        t = (topic or "Topic").replace("\\", " ").replace("\"", "\'")[:160]
        g = (grade_level or "4").replace("\"", "\'")[:6]
        # Many labeled segments with self.wait() so the MP4 runs for several minutes.
        return f'''from manim import *

class ExplanationScene(Scene):
    def construct(self):
        tstr = {repr(t)}
        gstr = {repr(g)}

        title = Text("Lesson: " + tstr, font_size=42, color=BLUE, line_spacing=0.6)
        sub = Text("Grade " + gstr + "  |  Long walkthrough, take your time", font_size=22, color=GRAY)
        sub.next_to(title, DOWN)
        self.play(Write(title), run_time=1.6)
        self.play(Write(sub), run_time=1.2)
        self.wait(8)

        self.play(FadeOut(VGroup(title, sub)))

        steps = [
            "1. We start with the main idea, slowly.",
            "2. A simple example to anchor the idea.",
            "3. A second look from another angle.",
            "4. Visual labels and a short number example.",
            "5. A step-by-step read through the logic.",
            "6. A second number example, still slow.",
            "7. If this feels easy, the next one stretches a little.",
            "8. A picture made from shapes (informal, not a strict diagram).",
            "9. A check: does this still match the idea?",
            "10. A place where people often get confused.",
            "11. A way to re-check your own work.",
            "12. A different wording of the same idea.",
            "13. A small recap of what changed between steps.",
            "14. One more look at a worked line.",
            "15. A slower pause before the summary.",
        ]

        for j, st in enumerate(steps, start=1):
            head = Text(st, font_size=30, color=YELLOW)
            body = Text("Read, pause, rewind the video if you need to.", font_size=24, color=WHITE)
            body.next_to(head, DOWN, buff=0.35)
            g2 = VGroup(head, body).to_edge(UP, buff=0.45)
            self.play(Write(g2), run_time=1.7)
            if j in (2, 6, 8, 12, 15):
                ex = Text("1 + 1 = 2   (we keep simple math as a stand-in for any worked line)", font_size=22, color=GREEN)
                ex.next_to(g2, DOWN, buff=0.6)
                self.play(Write(ex), run_time=1.2)
                self.wait(9)
                self.play(FadeOut(ex))
            else:
                self.wait(9)
            if j in (3, 9, 14, 5):
                extra = Text("Breathe, then continue.", font_size=22, color=ORANGE)
                extra.next_to(g2, DOWN, buff=0.6)
                self.play(FadeIn(extra), run_time=1.0)
                self.wait(7)
                self.play(FadeOut(VGroup(g2, extra)))
            else:
                self.play(FadeOut(g2), run_time=0.6)

        tail = Text("This fallback clip is long on purpose. Ask the API to tune MANIM_TARGET_MINUTES.", font_size=20, color=TEAL)
        self.play(Write(tail), run_time=1.2)
        self.wait(5)
        self.play(FadeOut(tail))
        out = Text("You reached the end of the walkthrough.", font_size=32, color=BLUE)
        self.play(Write(out), run_time=1.5)
        self.wait(6)
        self.play(FadeOut(out))
'''
    
    async def _generate_manim_script(
        self,
        topic: str,
        grade_level: str,
        student_profile: StudentProfile,
        language: str,
        extra_context: Optional[str] = None,
        narration_excerpt: str = "none",
    ) -> str:
        """Generate Manim script with Gemini (via llm_service)."""
        tmin = self._target_minutes
        ex_raw = (extra_context or "").strip() or "none"
        ex = ex_raw.replace("{", "{{").replace("}", "}}")[:4000]
        ne = (narration_excerpt or "none").replace("{", "{{").replace("}", "}}")
        if len(ne) > 12000:
            ne = ne[:12000] + "…"

        def _pat_dict(obj, key: str) -> dict:
            d = getattr(obj, key, None)
            return d if isinstance(d, dict) else {}

        profile_summary = {
            "learning_style": self._ls_style(student_profile),
            "confusion_areas": list(_pat_dict(student_profile, "confusion_patterns").keys())[:3],
            "success_areas": list(_pat_dict(student_profile, "success_patterns").keys())[:3],
        }

        # Calculate minimum wait time for production quality
        wait_time_minimum = int(60 * tmin * 0.4)  # 40% of target time in wait calls
        
        prompt = self.manim_prompt_template.format(
            topic=topic,
            grade_level=grade_level,
            language=language,
            target_minutes=f"{tmin:.1f}",
            wait_time_minimum=wait_time_minimum,
            narration_excerpt=ne,
            extra_context=ex,
            student_profile_summary=json.dumps(profile_summary),
        )
        if not self.llm:
            logger.warning("No LLM; using long local lesson script")
            return self._create_long_lesson_script(topic, grade_level)
        try:
            logger.debug("Generating Manim script for %s...", topic)
            response_text = await self.llm.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=8192,
            )
            if self._is_bad_manim_text(response_text):
                logger.warning("LLM Manim output unusable; using long lesson fallback")
                return self._create_long_lesson_script(topic, grade_level)
            script = self._extract_python_code(response_text)
            if self._is_bad_manim_text(script):
                logger.warning("Extracted Manim script invalid; using long lesson fallback")
                return self._create_long_lesson_script(topic, grade_level)
            return script
        except Exception as e:
            logger.error("Error generating Manim script: %s", e)
            return self._create_long_lesson_script(topic, grade_level)
    
    def _extract_python_code(self, response_text: str) -> str:
        """Extract Python code from Gemini response"""
        try:
            # Remove markdown code blocks
            import re
            
            # Look for python code blocks
            python_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
            if python_match:
                return python_match.group(1)
            
            # Look for any code blocks
            code_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
            if code_match:
                return code_match.group(1)
            
            # If no code blocks, assume entire response is code
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting Python code: {str(e)}")
            return response_text
    
    def _validate_manim_script(self, script: str) -> bool:
        """Validate Manim script for basic syntax"""
        try:
            if not self._manim_has_import(script):
                logger.warning("Missing or invalid manim import")
                return False
            required_elements = [
                "class ",
                "Scene",
                "def construct(self):"
            ]
            
            for element in required_elements:
                if element not in script:
                    logger.warning(f"Missing required element: {element}")
                    return False
            
            # Try to compile the script
            compile(script, '<string>', 'exec')
            
            return True
            
        except SyntaxError as e:
            logger.error(f"Syntax error in Manim script: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error validating script: {str(e)}")
            return False
    
    async def _fix_manim_script(self, broken_script: str, topic: str) -> str:
        """Attempt to fix broken Manim script using LLM"""
        try:
            if not self.llm:
                return self._create_long_lesson_script(topic, "4")
            
            fix_prompt = f"""The following Manim script has syntax errors. Please fix it and return only the corrected Python code:

```python
{broken_script}
```

Requirements:
1. Fix all syntax errors
2. Ensure all imports are correct
3. Make sure the class extends Scene
4. Verify the construct method is properly defined
5. Return ONLY valid Python code with no explanations"""

            response_text = await self.llm.generate(
                prompt=fix_prompt,
                temperature=0.4,
                max_tokens=8000,
            )
            
            fixed_script = self._extract_python_code(response_text)
            
            if self._validate_manim_script(fixed_script) and not self._is_bad_manim_text(fixed_script):
                logger.info("Manim script fixed successfully")
                return fixed_script
            else:
                logger.warning("Fixed script still has issues; using long local lesson")
                return self._create_long_lesson_script(topic, "4")
                
        except Exception as e:
            logger.error(f"Error fixing Manim script: {str(e)}")
            return self._create_long_lesson_script(topic, "4")
    
    def _create_fallback_script(self, topic: str, grade_level: str) -> str:
        """Create a simple fallback Manim script"""
        return f'''from manim import *

class ExplanationScene(Scene):
    def construct(self):
        # Title
        title = Text("{topic}", font_size=48, color=BLUE)
        subtitle = Text("Educational Video", font_size=24, color=WHITE)
        subtitle.next_to(title, DOWN)
        
        self.play(Write(title))
        self.play(Write(subtitle))
        self.wait(2)
        
        # Clear screen
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Main content
        content = Text("Let's learn about {topic}!", font_size=36, color=GREEN)
        self.play(Write(content))
        self.wait(2)
        
        # Example or explanation
        explanation = Text("This is an important concept\\nfor grade {grade_level} students.", font_size=28, color=YELLOW)
        explanation.next_to(content, DOWN, buff=1)
        self.play(Write(explanation))
        self.wait(3)
        
        # Summary
        self.play(FadeOut(content), FadeOut(explanation))
        summary = Text("Great job learning about {topic}!", font_size=32, color=BLUE)
        self.play(Write(summary))
        self.wait(2)
        
        # End
        self.play(FadeOut(summary))'''
    
    async def _render_manim_video(
        self,
        script: str,
        topic: str,
        target_duration_minutes: float = 5.0,
    ) -> Dict[str, Any]:
        """Render video using Manim subprocess"""
        try:
            tmin = max(2.0, float(target_duration_minutes or 4.0))
            # Subprocess: no cap by default (user asked not to time-limit long Manim work).
            # If you need a guardrail, set MANIM_SUBPROCESS_TIMEOUT_SEC to a positive value (seconds only).
            raw = (os.getenv("MANIM_SUBPROCESS_TIMEOUT_SEC") or "").strip()
            if raw == "" or raw in ("0", "none", "None"):
                render_timeout = None
            else:
                try:
                    v = int(float(raw))
                    render_timeout = v if v > 0 else None
                except ValueError:
                    render_timeout = None
            # Create unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_filename = f"scene_{timestamp}.py"
            video_id = f"video_{timestamp}"
            
            # Write script to temporary file
            script_path = self.temp_dir / script_filename
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Prepare Manim command
            output_dir = self.videos_dir
            manim_cmd = [
                sys.executable, "-m", "manim",
                str(script_path),
                "ExplanationScene",  # Default scene class name
                "-o", f"{video_id}.mp4",
                "--media_dir", str(output_dir),
                "-v", "WARNING",  # Reduce verbosity
                "--disable_caching"
            ]
            
            # Record start time
            start_time = datetime.now()
            
            if render_timeout is None:
                logger.info("Running Manim (no subprocess timeout; set MANIM_SUBPROCESS_TIMEOUT_SEC to cap):")
            else:
                logger.info("Running Manim (subprocess timeout %ss):", render_timeout)
            logger.info("Command: %s", " ".join(manim_cmd))
            
            try:
                run_kw = {
                    "cwd": str(self.temp_dir),
                    "capture_output": True,
                    "text": True,
                }
                if render_timeout is not None:
                    run_kw["timeout"] = render_timeout
                result = await asyncio.to_thread(subprocess.run, manim_cmd, **run_kw)
                stdout = result.stdout
                stderr = result.stderr
                returncode = result.returncode
            except subprocess.TimeoutExpired as te:
                raise Exception(
                    f"Manim hit subprocess timeout after {getattr(te, 'timeout', None) or render_timeout}s. "
                    "Increase MANIM_SUBPROCESS_TIMEOUT_SEC, or set it to 0 to disable, then simplify the scene if needed."
                ) from te
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Check if rendering was successful
            if returncode != 0:
                error_msg = stderr or stdout or "Unknown Manim error"
                logger.error(f"Manim rendering failed: {error_msg}")
                raise Exception(f"Manim rendering failed: {error_msg}")
            
            # Find the generated video file
            video_file = self._find_generated_video(output_dir, video_id)
            
            if not video_file:
                raise Exception("Video file not found after rendering")
            
            # Get video information
            file_size_mb = video_file.stat().st_size / (1024 * 1024)
            video_duration = await self._get_video_duration(video_file)
            
            # Create public URL
            video_url = f"/videos/{video_file.name}"
            
            # Clean up temporary script
            try:
                script_path.unlink()
            except Exception:
                pass
            
            logger.info(f"Video generated successfully: {video_file.name}")
            
            return {
                "video_url": video_url,
                "video_id": video_id,
                "topic": topic,
                "duration_seconds": video_duration,
                "file_size_mb": round(file_size_mb, 2),
                "manim_script": script,
                "generation_time_seconds": round(generation_time, 2),
                "local_video_path": str(video_file),
                "has_audio": False,
                "tts_engine": None,
                "narration_preview": None,
            }
            
        except Exception as e:
            logger.error(f"Error rendering video: {str(e)}")
            raise Exception(f"Video rendering failed: {str(e)}")
    
    def _find_generated_video(self, output_dir: Path, video_id: str) -> Optional[Path]:
        """Find the generated video file"""
        try:
            # Manim typically creates videos in videos/scene_name/quality/ structure
            possible_paths = [
                output_dir / f"{video_id}.mp4",
                output_dir / "videos" / "scene" / "1080p60" / f"{video_id}.mp4",
                output_dir / "videos" / "ExplanationScene" / "1080p60" / f"{video_id}.mp4"
            ]
            
            # Also search recursively for any mp4 files created in the last minute
            for video_file in output_dir.rglob("*.mp4"):
                if video_file.stat().st_mtime > (datetime.now().timestamp() - 60):  # Created in last minute
                    # Move to main videos directory with our naming
                    new_name = output_dir / f"{video_id}.mp4"
                    if video_file != new_name:
                        video_file.rename(new_name)
                    return new_name
            
            for path in possible_paths:
                if path.exists():
                    return path
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding generated video: {str(e)}")
            return None
    
    async def _get_video_duration(self, video_path: Path) -> Optional[float]:
        """Get video duration using ffprobe if available"""
        try:
            cmd = [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "csv=p=0", str(video_path)
            ]
            
            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                return duration
            
        except Exception as e:
            logger.debug(f"Could not get video duration: {str(e)}")
        
        return None
    
    def _create_fallback_video_response(self, topic: str, error: str) -> VideoResponse:
        """No placeholder file: empty URL; client should show the error. Successful renders live under /videos/"""
        safe = (error or "unknown")[:2000]
        return VideoResponse(
            video_url="",
            video_id=f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=topic,
            duration_seconds=None,
            file_size_mb=None,
            manim_script=f"# Video generation failed: {safe}",
            generation_time_seconds=0.0,
            has_audio=False,
            tts_engine=None,
            narration_preview=f"Generation did not complete: {safe}",
        )
    
    def is_healthy(self) -> bool:
        """Check if Manim generator is healthy"""
        try:
            # Check if Manim is available
            result = subprocess.run(
                [sys.executable, "-m", "manim", "--version"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    async def cleanup_old_videos(self, days_old: int = 7):
        """Clean up old video files to save space"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            
            for video_file in self.videos_dir.glob("*.mp4"):
                if video_file.stat().st_mtime < cutoff_time:
                    try:
                        video_file.unlink()
                        logger.info(f"Cleaned up old video: {video_file.name}")
                    except Exception as e:
                        logger.warning(f"Could not delete {video_file.name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error cleaning up videos: {str(e)}")