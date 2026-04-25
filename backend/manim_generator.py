"""
Manim Video Generator for SnapLearn AI
Generates educational videos using Manim locally as subprocess
"""

import os
import logging
import subprocess
import json
import tempfile
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from models import VideoResponse, StudentProfile

logger = logging.getLogger(__name__)

class ManimGenerator:
    """Generates educational videos using Manim"""
    
    def __init__(self):
        self.videos_dir = Path("../videos")
        self.temp_dir = Path("../temp_manim")
        self.prompts_dir = Path("../prompts")
        
        # Create directories
        self.videos_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize Gemini client for script generation
        self.gemini_client = None
        self.model_name = "gemini-3-flash-preview"
        
        # Create manim scene prompt template
        self._create_manim_prompt_template()
        
        # Initialize Gemini
        asyncio.create_task(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini client for script generation"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for video script generation")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Manim generator: Gemini client initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for video generation")
        except Exception as e:
            logger.error(f"Error initializing Gemini for video generation: {str(e)}")
    
    def _create_manim_prompt_template(self):
        """Create the Manim scene generation prompt template"""
        prompt_template = """You are an expert at creating Manim scene scripts for educational videos.

STUDENT CONTEXT:
- Grade Level: {grade_level}
- Topic: {topic}
- Language: {language}
- Student Learning Profile: {student_profile_summary}

REQUIREMENTS:
1. Create a complete Manim scene script for grade {grade_level}
2. Use only Manim Community Edition v0.18+ APIs
3. The script must be syntactically correct Python
4. Include engaging animations appropriate for the grade level
5. Use simple vocabulary for lower grades, more advanced for higher grades
6. Include worked examples where relevant

MANIM SCRIPT REQUIREMENTS:
- Extend the Scene class
- Include title card opening
- Divide explanation into 4-6 distinct animation scenes
- Use MathTex for mathematical notation
- Use Write() for text animations and Create() for shapes
- Include at least one step-by-step worked example
- Set appropriate self.wait() between scenes
- End with a summary slide
- Use colors that are engaging but not overwhelming

RESPONSE FORMAT:
Return ONLY the Python code for the Manim scene, no explanations or markdown.

Example structure:
```python
from manim import *

class ExplanationScene(Scene):
    def construct(self):
        # Title card
        title = Text("{topic}", font_size=48, color=BLUE)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        
        # Main content scenes...
        # Include worked examples...
        # Summary scene...
```

Generate the Manim script for topic: {topic}"""
        
        # Save the prompt template
        prompt_file = self.prompts_dir / "manim_scene.txt"
        prompt_file.parent.mkdir(exist_ok=True)
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_template)
        
        self.manim_prompt_template = prompt_template
    
    async def generate_video(self, topic: str, grade_level: str, 
                           student_profile: StudentProfile, language: str = "en") -> VideoResponse:
        """Generate educational video for given topic"""
        try:
            logger.info(f"Starting video generation for topic: {topic}")
            
            # Generate Manim script using Gemini
            manim_script = await self._generate_manim_script(
                topic, grade_level, student_profile, language
            )
            
            if not manim_script:
                raise Exception("Failed to generate Manim script")
            
            # Validate the script
            if not self._validate_manim_script(manim_script):
                # Try to fix the script
                manim_script = await self._fix_manim_script(manim_script, topic)
            
            # Create video using Manim
            video_info = await self._render_manim_video(manim_script, topic)
            
            return VideoResponse(**video_info)
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            return self._create_fallback_video_response(topic, str(e))
    
    async def _generate_manim_script(self, topic: str, grade_level: str, 
                                   student_profile: StudentProfile, language: str) -> str:
        """Generate Manim script using Gemini API"""
        try:
            if not self.gemini_client:
                return self._create_fallback_script(topic, grade_level)
            
            # Prepare student profile summary
            profile_summary = {
                "learning_style": student_profile.learning_style.value,
                "confusion_areas": list(student_profile.confusion_patterns.keys())[:3],
                "success_areas": list(student_profile.success_patterns.keys())[:3]
            }
            
            # Format the prompt
            prompt = self.manim_prompt_template.format(
                topic=topic,
                grade_level=grade_level,
                language=language,
                student_profile_summary=json.dumps(profile_summary)
            )
            
            # Call Gemini API
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract Python code from response
            script = self._extract_python_code(response.text)
            
            logger.info("Manim script generated successfully")
            return script
            
        except Exception as e:
            logger.error(f"Error generating Manim script: {str(e)}")
            return self._create_fallback_script(topic, grade_level)
    
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
            # Check for basic Manim requirements
            required_elements = [
                "from manim import",
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
        """Attempt to fix broken Manim script using Gemini"""
        try:
            if not self.gemini_client:
                return self._create_fallback_script(topic, "4")
            
            fix_prompt = f"""The following Manim script has syntax errors. Please fix it and return only the corrected Python code:

```python
{broken_script}
```

Requirements:
1. Fix all syntax errors
2. Ensure all imports are correct
3. Make sure the class extends Scene
4. Verify the construct method is properly defined
5. Return ONLY the corrected Python code

Fixed script:"""
            
            response = self.gemini_client.models.generate_content(
                model=self.model_name,
                contents=fix_prompt
            )
            
            fixed_script = self._extract_python_code(response.text)
            
            # Validate the fixed script
            if self._validate_manim_script(fixed_script):
                logger.info("Successfully fixed Manim script")
                return fixed_script
            else:
                logger.warning("Fixed script still has issues, using fallback")
                return self._create_fallback_script(topic, "4")
                
        except Exception as e:
            logger.error(f"Error fixing Manim script: {str(e)}")
            return self._create_fallback_script(topic, "4")
    
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
    
    async def _render_manim_video(self, script: str, topic: str) -> Dict[str, Any]:
        """Render video using Manim subprocess"""
        try:
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
                "python", "-m", "manim",
                str(script_path),
                "ExplanationScene",  # Default scene class name
                "-o", f"{video_id}.mp4",
                "--media_dir", str(output_dir),
                "-v", "WARNING",  # Reduce verbosity
                "--disable_caching"
            ]
            
            # Record start time
            start_time = datetime.now()
            
            # Run Manim subprocess
            logger.info(f"Running Manim command: {' '.join(manim_cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *manim_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)  # 5 minute timeout
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception("Manim rendering timed out after 5 minutes")
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
            # Check if rendering was successful
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown Manim error"
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
                "generation_time_seconds": round(generation_time, 2)
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
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await process.communicate()
            
            if process.returncode == 0:
                duration = float(stdout.decode().strip())
                return duration
            
        except Exception as e:
            logger.debug(f"Could not get video duration: {str(e)}")
        
        return None
    
    def _create_fallback_video_response(self, topic: str, error: str) -> VideoResponse:
        """Create fallback video response when generation fails"""
        return VideoResponse(
            video_url="/static/placeholder_video.mp4",  # Could create a placeholder
            video_id=f"failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            topic=topic,
            duration_seconds=None,
            file_size_mb=None,
            manim_script=f"# Video generation failed: {error}",
            generation_time_seconds=0.0
        )
    
    def is_healthy(self) -> bool:
        """Check if Manim generator is healthy"""
        try:
            # Check if Manim is available
            result = subprocess.run(
                ["python", "-m", "manim", "--version"],
                capture_output=True,
                text=True,
                timeout=10
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