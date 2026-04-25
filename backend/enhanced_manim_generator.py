"""
Enhanced Manim Video Generator for SnapLearn AI - Phase 4
Advanced educational video generation with conversation context integration
"""

import os
import logging
import subprocess
import json
import tempfile
import asyncio
import hashlib
import shutil
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum

from models import (
    VideoResponse, 
    StudentProfile, 
    ConversationResponse,
    LearningAnalytics
)

logger = logging.getLogger(__name__)

class VideoQuality(str, Enum):
    """Video quality options"""
    LOW = "480p30"       # 480p at 30fps
    MEDIUM = "720p30"    # 720p at 30fps  
    HIGH = "1080p60"     # 1080p at 60fps
    ULTRA = "1440p60"    # 1440p at 60fps

class VideoFormat(str, Enum):
    """Video format options"""
    MP4 = "mp4"
    MOV = "mov"
    WEBM = "webm"
    GIF = "gif"

class AnimationStyle(str, Enum):
    """Animation style preferences"""
    CLASSIC = "classic"           # Traditional blackboard style
    MODERN = "modern"             # Clean, minimalist animations
    COLORFUL = "colorful"         # Bright, engaging colors
    MATHEMATICAL = "mathematical" # Focus on equations and formulas
    VISUAL = "visual"             # Heavy use of diagrams and graphics
    KINESTHETIC = "kinesthetic"   # Movement-based explanations

class EnhancedManimGenerator:
    """Enhanced Manim generator with advanced features and conversation integration"""
    
    def __init__(self):
        self.videos_dir = Path("../videos")
        self.temp_dir = Path("../temp_manim")
        self.thumbnails_dir = Path("../thumbnails")
        self.scripts_cache_dir = Path("../manim_scripts")
        
        # Create directories
        for directory in [self.videos_dir, self.temp_dir, self.thumbnails_dir, self.scripts_cache_dir]:
            directory.mkdir(exist_ok=True)
        
        # Initialize Gemini client
        self.gemini_client = None
        
        # Video generation queue for batch processing
        self.generation_queue = []
        self.is_processing_batch = False
        
        # Analytics tracking
        self.generation_analytics = {}
        
        # Advanced prompting templates
        self._init_advanced_prompts()
        
        # Initialize Gemini with Interactions API
        asyncio.create_task(self._init_gemini())
    
    async def _init_gemini(self):
        """Initialize Gemini Interactions API client"""
        try:
            from google import genai
            
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("Gemini API key not found for enhanced video generation")
                return
            
            self.gemini_client = genai.Client(api_key=api_key)
            logger.info("Enhanced Manim generator: Gemini Interactions API initialized")
            
        except ImportError:
            logger.error("Google GenAI library not installed for enhanced video generation")
        except Exception as e:
            logger.error(f"Error initializing Gemini for enhanced video generation: {str(e)}")
    
    def _init_advanced_prompts(self):
        """Initialize advanced prompting templates for different scenarios"""
        
        # Base system instruction for all video generation
        self.system_instruction = """You are an expert educational video creator specializing in Manim animations. Your goal is to create engaging, pedagogically sound animated explanations that adapt to individual student needs and learning contexts.

CORE PRINCIPLES:
1. Pedagogical Effectiveness: Build understanding step-by-step with clear progressions
2. Visual Clarity: Use animations that enhance rather than distract from learning
3. Adaptive Content: Adjust complexity, pace, and style based on student data
4. Engagement: Create memorable visual narratives that maintain attention
5. Mathematical Precision: Ensure all mathematical content is accurate and well-formatted

MANIM EXPERTISE:
- Use Manim Community Edition v0.18+ syntax and best practices
- Leverage advanced animation techniques for smooth, professional results
- Implement proper scene transitions and pacing
- Use appropriate color schemes and visual hierarchies
- Create mathematically accurate diagrams and animations

PERSONALIZATION:
- Adapt explanation depth to grade level and student confusion patterns
- Use visual styles that match student learning preferences
- Incorporate examples relevant to student success areas
- Address known misconceptions proactively"""

        # Context-aware script generation template
        self.context_aware_template = """Generate a Manim video script that leverages the following learning context:

STUDENT LEARNING CONTEXT:
- Grade Level: {grade_level}
- Learning Style: {learning_style}
- Current Topic: {topic}
- Difficulty Level: {difficulty_level}
- Recent Confusion Areas: {confusion_patterns}
- Success Patterns: {success_patterns}

CONVERSATION CONTEXT:
- Recent Questions: {recent_questions}
- Explanation Style Used: {explanation_style}
- Key Concepts Covered: {key_concepts}
- Follow-up Areas: {follow_up_areas}

ADAPTIVE REQUIREMENTS:
- Difficulty: {difficulty_level}
- Animation Style: {animation_style}
- Pace: {pacing_preference}
- Focus Areas: {focus_areas}

VIDEO SPECIFICATIONS:
- Duration Target: {target_duration} seconds
- Quality: {video_quality}
- Mathematical Notation Level: {math_complexity}

Create a Manim script that:
1. Builds on the conversation context and addresses identified learning needs
2. Uses the specified difficulty level and animation style
3. Incorporates successful learning patterns from the student's history
4. Addresses confusion areas with targeted visual explanations
5. Includes interactive elements appropriate for the learning style
6. Follows professional animation principles with smooth transitions

RESPONSE FORMAT: Return only the complete Python Manim script, properly formatted and syntactically correct."""

        # Batch generation template for learning paths
        self.batch_generation_template = """Generate a series of interconnected Manim video scripts for a learning path:

LEARNING PATH CONTEXT:
- Student Profile: {student_profile}
- Learning Sequence: {learning_sequence}
- Total Duration: {total_duration} minutes
- Difficulty Progression: {difficulty_progression}

INDIVIDUAL VIDEO REQUIREMENTS:
{video_requirements}

Create {num_videos} interconnected scripts that:
1. Build knowledge progressively across videos
2. Reference previous concepts appropriately
3. Maintain visual and narrative consistency
4. Include smooth conceptual transitions
5. Adapt difficulty as specified in the progression

Return as JSON array of scripts with metadata."""

        # Mathematical animation specialists
        self.math_animation_template = """Create advanced mathematical animations for: {topic}

MATHEMATICAL REQUIREMENTS:
- Concept Level: {math_level}
- Visualization Type: {visualization_type}
- Interactive Elements: {interactive_elements}
- Proof/Derivation Depth: {proof_depth}

ANIMATION SPECIFICATIONS:
- Use MathTex for all mathematical expressions
- Implement step-by-step derivations with Transform animations
- Include interactive problem-solving segments
- Show multiple solution approaches when applicable
- Use color coding for mathematical relationships

Generate sophisticated mathematical visualizations that make abstract concepts concrete."""

    async def generate_contextual_video(self, 
                                      topic: str,
                                      student_profile: StudentProfile,
                                      conversation_context: Optional[ConversationResponse] = None,
                                      learning_analytics: Optional[LearningAnalytics] = None,
                                      video_quality: VideoQuality = VideoQuality.HIGH,
                                      video_format: VideoFormat = VideoFormat.MP4,
                                      animation_style: AnimationStyle = AnimationStyle.MODERN,
                                      target_duration: int = 180) -> Dict[str, Any]:
        """Generate video with full conversation and learning context integration"""
        try:
            logger.info(f"Generating contextual video for topic: {topic}")
            
            # Analyze learning context
            learning_context = await self._analyze_learning_context(
                student_profile, conversation_context, learning_analytics
            )
            
            # Generate advanced script using conversation context
            script_data = await self._generate_context_aware_script(
                topic=topic,
                learning_context=learning_context,
                animation_style=animation_style,
                target_duration=target_duration,
                video_quality=video_quality
            )
            
            if not script_data:
                raise Exception("Failed to generate contextual script")
            
            # Create multiple quality versions if requested
            video_variants = await self._render_video_variants(
                script_data["script"],
                topic,
                [video_quality],  # Can expand to multiple qualities
                [video_format]
            )
            
            # Generate smart thumbnail
            thumbnail_path = await self._generate_smart_thumbnail(
                script_data["script"], 
                topic, 
                learning_context
            )
            
            # Create video analytics baseline
            video_analytics = await self._initialize_video_analytics(
                topic, student_profile, learning_context, script_data
            )
            
            # Prepare comprehensive response
            video_response = {
                "video_url": video_variants[0]["video_url"],
                "video_id": video_variants[0]["video_id"], 
                "topic": topic,
                "duration_seconds": video_variants[0]["duration_seconds"],
                "file_size_mb": video_variants[0]["file_size_mb"],
                "manim_script": script_data["script"],
                "generation_time_seconds": video_variants[0]["generation_time_seconds"],
                
                # Phase 4 enhancements
                "video_variants": video_variants,
                "thumbnail_url": f"/thumbnails/{thumbnail_path.name}" if thumbnail_path else None,
                "learning_context": learning_context,
                "script_metadata": script_data["metadata"],
                "animation_style": animation_style.value,
                "difficulty_level": learning_context["current_difficulty"],
                "personalization_applied": learning_context["personalizations"],
                "video_analytics": video_analytics,
                "conceptual_map": script_data.get("conceptual_map", []),
                "interactive_elements": script_data.get("interactive_elements", [])
            }
            
            return video_response
            
        except Exception as e:
            logger.error(f"Error generating contextual video: {str(e)}")
            raise Exception(f"Enhanced video generation failed: {str(e)}")
    
    async def _analyze_learning_context(self, 
                                       student_profile: StudentProfile,
                                       conversation_context: Optional[ConversationResponse],
                                       learning_analytics: Optional[LearningAnalytics]) -> Dict[str, Any]:
        """Analyze comprehensive learning context for video personalization"""
        
        context = {
            "student_profile": {
                "grade_level": student_profile.grade_level.value,
                "learning_style": student_profile.learning_style.value,
                "confusion_patterns": list(student_profile.confusion_patterns.keys())[:5],
                "success_patterns": list(student_profile.success_patterns.keys())[:5]
            },
            "conversation_insights": {},
            "learning_insights": {},
            "personalizations": []
        }
        
        # Extract conversation context
        if conversation_context:
            context["conversation_insights"] = {
                "recent_questions": [conversation_context.response.explanation_text[:100]],
                "explanation_style": getattr(conversation_context.response, 'explanation_style', 'balanced'),
                "key_concepts": conversation_context.response.key_concepts,
                "difficulty_level": conversation_context.response.difficulty_level,
                "follow_up_areas": conversation_context.response.follow_up_questions[:3],
                "engagement_level": conversation_context.learning_insights.get("engagement_level", 0.7)
            }
        
        # Extract learning analytics
        if learning_analytics:
            context["learning_insights"] = {
                "total_time_minutes": learning_analytics.total_time_minutes,
                "concepts_mastered": learning_analytics.concepts_mastered,
                "accuracy_metrics": learning_analytics.accuracy_metrics,
                "learning_velocity": learning_analytics.learning_velocity,
                "engagement_trend": learning_analytics.engagement_metrics
            }
        
        # Determine personalizations to apply
        personalizations = []
        
        if student_profile.learning_style.value == "visual":
            personalizations.extend(["enhanced_diagrams", "color_coding", "step_by_step_visuals"])
        elif student_profile.learning_style.value == "kinesthetic":
            personalizations.extend(["interactive_elements", "movement_based", "hands_on_examples"])
        elif student_profile.learning_style.value == "auditory":
            personalizations.extend(["narrative_structure", "rhythm_based", "verbal_explanations"])
        
        # Difficulty adaptations
        if context["conversation_insights"].get("difficulty_level") == "easy":
            personalizations.extend(["simplified_language", "more_examples", "slower_pace"])
        elif context["conversation_insights"].get("difficulty_level") == "hard":
            personalizations.extend(["advanced_concepts", "mathematical_rigor", "faster_pace"])
        
        # Confusion pattern adaptations
        confusion_areas = student_profile.confusion_patterns
        if confusion_areas:
            most_confused = max(confusion_areas.keys(), key=confusion_areas.get)
            personalizations.append(f"address_{most_confused}_confusion")
        
        context["personalizations"] = personalizations
        context["current_difficulty"] = context["conversation_insights"].get("difficulty_level", "medium")
        
        return context
    
    async def _generate_context_aware_script(self, 
                                           topic: str,
                                           learning_context: Dict[str, Any],
                                           animation_style: AnimationStyle,
                                           target_duration: int,
                                           video_quality: VideoQuality) -> Dict[str, Any]:
        """Generate Manim script using comprehensive learning context"""
        try:
            if not self.gemini_client:
                return await self._create_enhanced_fallback_script(topic, learning_context)
            
            # Build comprehensive prompt with learning context
            prompt = self.context_aware_template.format(
                topic=topic,
                grade_level=learning_context["student_profile"]["grade_level"],
                learning_style=learning_context["student_profile"]["learning_style"],
                difficulty_level=learning_context["current_difficulty"],
                confusion_patterns=", ".join(learning_context["student_profile"]["confusion_patterns"]),
                success_patterns=", ".join(learning_context["student_profile"]["success_patterns"]),
                recent_questions=", ".join(learning_context["conversation_insights"].get("recent_questions", [""])),
                explanation_style=learning_context["conversation_insights"].get("explanation_style", "balanced"),
                key_concepts=", ".join(learning_context["conversation_insights"].get("key_concepts", [])),
                follow_up_areas=", ".join(learning_context["conversation_insights"].get("follow_up_areas", [])),
                animation_style=animation_style.value,
                pacing_preference=self._determine_pacing(learning_context),
                focus_areas=", ".join(learning_context["personalizations"]),
                target_duration=target_duration,
                video_quality=video_quality.value,
                math_complexity=self._determine_math_complexity(learning_context)
            )
            
            # Use Gemini Interactions API for script generation
            interaction = self.gemini_client.interactions.create(
                model="gemini-3.1-pro-preview",  # Use pro model for complex script generation
                input=prompt,
                system_instruction=self.system_instruction,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 3072  # Allow for longer scripts
                }
            )
            
            script_text = interaction.outputs[-1].text
            
            # Extract and validate script
            script = self._extract_python_code(script_text)
            
            if not self._validate_enhanced_script(script):
                # Try to fix the script
                script = await self._fix_enhanced_script(script, topic, learning_context)
            
            # Extract metadata from script analysis
            metadata = await self._analyze_script_metadata(script, learning_context)
            
            return {
                "script": script,
                "metadata": metadata,
                "conceptual_map": metadata.get("concepts_covered", []),
                "interactive_elements": metadata.get("interactive_points", []),
                "generation_context": learning_context
            }
            
        except Exception as e:
            logger.error(f"Error generating context-aware script: {str(e)}")
            return await self._create_enhanced_fallback_script(topic, learning_context)
    
    def _determine_pacing(self, learning_context: Dict[str, Any]) -> str:
        """Determine appropriate pacing based on learning context"""
        
        difficulty = learning_context["current_difficulty"]
        confusion_count = len(learning_context["student_profile"]["confusion_patterns"])
        learning_style = learning_context["student_profile"]["learning_style"]
        
        if difficulty == "easy" or confusion_count > 3:
            return "slow"
        elif difficulty == "hard" and confusion_count == 0:
            return "fast"
        elif learning_style in ["kinesthetic", "visual"]:
            return "medium_with_pauses"
        else:
            return "medium"
    
    def _determine_math_complexity(self, learning_context: Dict[str, Any]) -> str:
        """Determine mathematical notation complexity level"""
        
        grade_level = learning_context["student_profile"]["grade_level"]
        difficulty = learning_context["current_difficulty"]
        
        if grade_level in ["K", "1", "2"]:
            return "basic_arithmetic"
        elif grade_level in ["3", "4", "5"]:
            return "elementary_math"
        elif grade_level in ["6", "7", "8"]:
            return "middle_school_algebra" if difficulty != "easy" else "elementary_math"
        else:
            return "advanced_mathematics"
    
    async def _render_video_variants(self, 
                                   script: str,
                                   topic: str,
                                   qualities: List[VideoQuality],
                                   formats: List[VideoFormat]) -> List[Dict[str, Any]]:
        """Render video in multiple quality and format variants"""
        
        variants = []
        base_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, quality in enumerate(qualities):
            for j, format_type in enumerate(formats):
                try:
                    variant_id = f"{base_timestamp}_q{i}_f{j}"
                    
                    video_info = await self._render_single_variant(
                        script, topic, variant_id, quality, format_type
                    )
                    
                    if video_info:
                        variants.append(video_info)
                    
                except Exception as e:
                    logger.error(f"Error rendering variant {quality.value}/{format_type.value}: {str(e)}")
                    continue
        
        # If no variants succeeded, create fallback
        if not variants:
            variants.append(await self._create_fallback_variant(topic, base_timestamp))
        
        return variants
    
    async def _render_single_variant(self, 
                                   script: str,
                                   topic: str,
                                   variant_id: str,
                                   quality: VideoQuality,
                                   format_type: VideoFormat) -> Optional[Dict[str, Any]]:
        """Render a single video variant with specified quality and format"""
        try:
            # Create script file
            script_filename = f"scene_{variant_id}.py"
            script_path = self.temp_dir / script_filename
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Prepare Manim command with quality and format options
            output_filename = f"{variant_id}.{format_type.value}"
            manim_cmd = [
                "python", "-m", "manim",
                str(script_path),
                "ExplanationScene",
                "-o", output_filename,
                "--media_dir", str(self.videos_dir),
                "-v", "WARNING",
                "--disable_caching"
            ]
            
            # Add quality-specific flags
            if quality == VideoQuality.LOW:
                manim_cmd.extend(["-ql", "--fps", "30"])
            elif quality == VideoQuality.MEDIUM:
                manim_cmd.extend(["-qm", "--fps", "30"])
            elif quality == VideoQuality.HIGH:
                manim_cmd.extend(["-qh", "--fps", "60"])
            elif quality == VideoQuality.ULTRA:
                manim_cmd.extend(["--resolution", "2560,1440", "--fps", "60"])
            
            # Record start time
            start_time = datetime.now()
            
            # Run Manim rendering
            logger.info(f"Rendering {quality.value} {format_type.value} variant: {variant_id}")
            
            process = await asyncio.create_subprocess_exec(
                *manim_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # Wait for completion with extended timeout for higher qualities
            timeout = 600 if quality in [VideoQuality.HIGH, VideoQuality.ULTRA] else 300
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise Exception(f"Rendering timed out after {timeout} seconds")
            
            generation_time = (datetime.now() - start_time).total_seconds()
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown rendering error"
                raise Exception(f"Rendering failed: {error_msg}")
            
            # Find and process the generated video
            video_file = await self._find_and_move_video(variant_id, format_type)
            
            if not video_file:
                raise Exception("Video file not found after rendering")
            
            # Get video metadata
            file_size_mb = video_file.stat().st_size / (1024 * 1024)
            duration = await self._get_video_duration(video_file)
            
            # Clean up script file
            try:
                script_path.unlink()
            except Exception:
                pass
            
            return {
                "video_id": variant_id,
                "video_url": f"/videos/{video_file.name}",
                "quality": quality.value,
                "format": format_type.value,
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": duration,
                "generation_time_seconds": round(generation_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error rendering single variant: {str(e)}")
            return None
    
    async def _find_and_move_video(self, variant_id: str, format_type: VideoFormat) -> Optional[Path]:
        """Find generated video and move to proper location"""
        try:
            # Search for recently created video files
            target_extension = format_type.value
            target_filename = f"{variant_id}.{target_extension}"
            target_path = self.videos_dir / target_filename
            
            # Search in common Manim output directories
            search_dirs = [
                self.videos_dir,
                self.videos_dir / "videos",
                self.temp_dir
            ]
            
            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue
                    
                # Look for files created in the last 5 minutes
                cutoff_time = datetime.now().timestamp() - 300
                
                for video_file in search_dir.rglob(f"*.{target_extension}"):
                    if video_file.stat().st_mtime > cutoff_time:
                        # Move to target location
                        if video_file != target_path:
                            shutil.move(str(video_file), str(target_path))
                        return target_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding and moving video: {str(e)}")
            return None
    
    async def _generate_smart_thumbnail(self, 
                                      script: str,
                                      topic: str,
                                      learning_context: Dict[str, Any]) -> Optional[Path]:
        """Generate intelligent thumbnail based on video content and learning context"""
        try:
            # Extract key visual elements from script
            thumbnail_elements = await self._extract_thumbnail_elements(script, topic, learning_context)
            
            # Generate thumbnail script
            thumbnail_script = await self._create_thumbnail_script(thumbnail_elements, topic)
            
            if not thumbnail_script:
                return None
            
            # Render thumbnail as single frame
            thumbnail_id = f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            thumbnail_path = await self._render_thumbnail_image(thumbnail_script, thumbnail_id)
            
            return thumbnail_path
            
        except Exception as e:
            logger.error(f"Error generating smart thumbnail: {str(e)}")
            return None
    
    async def _extract_thumbnail_elements(self, 
                                        script: str,
                                        topic: str,
                                        learning_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key visual elements for thumbnail generation"""
        
        if not self.gemini_client:
            return {"title": topic, "elements": ["basic_title"]}
        
        try:
            thumbnail_prompt = f"""Analyze this Manim script and suggest the best thumbnail elements:

SCRIPT:
{script[:2000]}  # First 2000 chars

LEARNING CONTEXT:
- Topic: {topic}
- Grade Level: {learning_context["student_profile"]["grade_level"]}
- Learning Style: {learning_context["student_profile"]["learning_style"]}

Extract the most visually appealing and representative elements for a thumbnail that would:
1. Capture the main concept visually
2. Be appropriate for the grade level
3. Appeal to the learning style
4. Stand out as an educational video thumbnail

Return JSON format:
{{
  "main_title": "Primary text for thumbnail",
  "visual_elements": ["element1", "element2"],
  "color_scheme": "color palette recommendation",
  "mathematical_notation": "key equations or formulas to display",
  "grade_appropriate_style": "visual style recommendations"
}}"""

            interaction = self.gemini_client.interactions.create(
                model="gemini-3-flash-preview",
                input=thumbnail_prompt
            )
            
            response_text = interaction.outputs[-1].text
            
            # Parse JSON response
            try:
                if response_text.strip().startswith('{'):
                    return json.loads(response_text)
                else:
                    import re
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group(1))
            except:
                pass
            
            # Fallback
            return {
                "main_title": topic,
                "visual_elements": ["title", "basic_diagram"],
                "color_scheme": "blue_and_white",
                "mathematical_notation": "",
                "grade_appropriate_style": "clean_and_simple"
            }
            
        except Exception as e:
            logger.error(f"Error extracting thumbnail elements: {str(e)}")
            return {"title": topic, "elements": ["basic_title"]}
    
    async def _create_thumbnail_script(self, elements: Dict[str, Any], topic: str) -> str:
        """Create Manim script for thumbnail generation"""
        
        title = elements.get("main_title", topic)
        visual_elements = elements.get("visual_elements", ["title"])
        
        script = f'''from manim import *

class ThumbnailScene(Scene):
    def construct(self):
        # Background
        bg = Rectangle(width=16, height=9, fill_color=DARK_BLUE, fill_opacity=1)
        self.add(bg)
        
        # Main title
        title = Text("{title}", font_size=48, color=WHITE, weight=BOLD)
        title.move_to(UP * 1.5)
        self.add(title)
        
        # Visual elements based on content
        {"# Mathematical diagram" if "diagram" in visual_elements else ""}
        {"# Equation display" if "equation" in visual_elements else ""}
        {"# Grade level indicator" if "grade" in visual_elements else ""}
        
        # SnapLearn branding
        brand = Text("SnapLearn AI", font_size=24, color=YELLOW)
        brand.move_to(DOWN * 3.5 + RIGHT * 5)
        self.add(brand)
'''
        
        return script
    
    async def _render_thumbnail_image(self, script: str, thumbnail_id: str) -> Optional[Path]:
        """Render thumbnail as PNG image"""
        try:
            script_filename = f"thumbnail_{thumbnail_id}.py"
            script_path = self.temp_dir / script_filename
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script)
            
            # Render as single high-quality image
            cmd = [
                "python", "-m", "manim",
                str(script_path),
                "ThumbnailScene",
                "-s",  # Save last frame
                "--media_dir", str(self.thumbnails_dir),
                "-v", "WARNING"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            if process.returncode == 0:
                # Find and move thumbnail
                return await self._find_thumbnail_file(thumbnail_id)
            
        except Exception as e:
            logger.error(f"Error rendering thumbnail: {str(e)}")
        
        return None
    
    async def _find_thumbnail_file(self, thumbnail_id: str) -> Optional[Path]:
        """Find generated thumbnail file"""
        try:
            # Search for recently created PNG files
            cutoff_time = datetime.now().timestamp() - 60  # Last minute
            
            for png_file in self.thumbnails_dir.rglob("*.png"):
                if png_file.stat().st_mtime > cutoff_time:
                    # Rename to our convention
                    target_name = self.thumbnails_dir / f"{thumbnail_id}.png"
                    if png_file != target_name:
                        png_file.rename(target_name)
                    return target_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding thumbnail file: {str(e)}")
            return None
    
    async def _initialize_video_analytics(self, 
                                        topic: str,
                                        student_profile: StudentProfile,
                                        learning_context: Dict[str, Any],
                                        script_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize analytics tracking for the generated video"""
        
        analytics = {
            "video_id": script_data.get("video_id", "unknown"),
            "creation_date": datetime.now().isoformat(),
            "topic": topic,
            "student_grade": student_profile.grade_level.value,
            "personalization_applied": learning_context["personalizations"],
            "script_complexity": len(script_data["script"]),
            "concepts_covered": script_data.get("conceptual_map", []),
            "interactive_elements_count": len(script_data.get("interactive_elements", [])),
            "target_difficulty": learning_context["current_difficulty"],
            "learning_style_optimized": student_profile.learning_style.value,
            
            # Engagement prediction metrics
            "predicted_engagement": self._predict_engagement(learning_context, script_data),
            "confusion_risk_areas": learning_context["student_profile"]["confusion_patterns"],
            "success_amplifiers": learning_context["student_profile"]["success_patterns"],
            
            # Performance tracking (to be updated as video is watched)
            "views": 0,
            "completion_rate": 0.0,
            "rewatch_segments": [],
            "effectiveness_score": 0.0
        }
        
        # Store analytics for tracking
        analytics_id = f"analytics_{analytics['video_id']}"
        self.generation_analytics[analytics_id] = analytics
        
        return analytics
    
    def _predict_engagement(self, learning_context: Dict[str, Any], script_data: Dict[str, Any]) -> float:
        """Predict engagement score based on personalization and content"""
        
        base_score = 0.7
        
        # Boost for personalization
        personalizations = len(learning_context["personalizations"])
        personalization_boost = min(0.2, personalizations * 0.03)
        
        # Boost for interactive elements
        interactive_boost = min(0.1, len(script_data.get("interactive_elements", [])) * 0.02)
        
        # Adjust for difficulty match
        difficulty_match = 0.05 if learning_context["current_difficulty"] in ["medium", "easy"] else -0.05
        
        # Learning style alignment
        style_boost = 0.08 if "visual" in learning_context["personalizations"] else 0.04
        
        predicted_engagement = base_score + personalization_boost + interactive_boost + difficulty_match + style_boost
        
        return min(1.0, max(0.0, predicted_engagement))
    
    # Additional helper methods for enhanced functionality
    def _extract_python_code(self, response_text: str) -> str:
        """Enhanced Python code extraction with better parsing"""
        try:
            import re
            
            # Look for python code blocks first
            python_match = re.search(r'```python\s*(.*?)\s*```', response_text, re.DOTALL)
            if python_match:
                return python_match.group(1).strip()
            
            # Look for any code blocks
            code_match = re.search(r'```\s*(.*?)\s*```', response_text, re.DOTALL)
            if code_match:
                return code_match.group(1).strip()
            
            # If no code blocks, look for class definitions
            class_match = re.search(r'(class\s+\w+.*?(?=\n\s*$|\Z))', response_text, re.DOTALL | re.MULTILINE)
            if class_match:
                return class_match.group(1).strip()
            
            # Return entire response as fallback
            return response_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting Python code: {str(e)}")
            return response_text
    
    def _validate_enhanced_script(self, script: str) -> bool:
        """Enhanced script validation with Phase 4 requirements"""
        try:
            # Basic Manim requirements
            required_elements = [
                "from manim import",
                "class ",
                "Scene",
                "def construct(self):"
            ]
            
            # Check for required elements
            for element in required_elements:
                if element not in script:
                    logger.warning(f"Missing required element: {element}")
                    return False
            
            # Enhanced validation for Phase 4 features
            enhanced_checks = [
                "self.play(" in script,  # Must have animations
                "Text(" in script or "MathTex(" in script,  # Must have content
                "self.wait(" in script   # Must have proper timing
            ]
            
            if not any(enhanced_checks):
                logger.warning("Script lacks basic animation structure")
                return False
            
            # Syntax validation
            try:
                compile(script, '<string>', 'exec')
            except SyntaxError as e:
                logger.error(f"Syntax error in enhanced script: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating enhanced script: {str(e)}")
            return False
    
    async def _fix_enhanced_script(self, broken_script: str, topic: str, learning_context: Dict[str, Any]) -> str:
        """Enhanced script fixing with context awareness"""
        try:
            if not self.gemini_client:
                return await self._create_enhanced_fallback_script(topic, learning_context)
            
            fix_prompt = f"""Fix this Manim script while preserving the educational intent and personalization:

BROKEN SCRIPT:
```python
{broken_script}
```

LEARNING CONTEXT TO PRESERVE:
- Topic: {topic}
- Grade Level: {learning_context["student_profile"]["grade_level"]}
- Personalizations: {", ".join(learning_context["personalizations"])}

FIX REQUIREMENTS:
1. Correct all syntax errors
2. Ensure proper Manim v0.18+ syntax
3. Preserve educational content and personalization
4. Maintain appropriate grade level complexity
5. Include proper animations and timing

Return ONLY the corrected Python script."""

            interaction = self.gemini_client.interactions.create(
                model="gemini-3-flash-preview",
                input=fix_prompt
            )
            
            fixed_script = self._extract_python_code(interaction.outputs[-1].text)
            
            if self._validate_enhanced_script(fixed_script):
                logger.info("Successfully fixed enhanced script")
                return fixed_script
            else:
                logger.warning("Fixed script still has issues, using enhanced fallback")
                return await self._create_enhanced_fallback_script(topic, learning_context)
                
        except Exception as e:
            logger.error(f"Error fixing enhanced script: {str(e)}")
            return await self._create_enhanced_fallback_script(topic, learning_context)
    
    async def _create_enhanced_fallback_script(self, topic: str, learning_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create sophisticated fallback script with learning context"""
        
        grade_level = learning_context["student_profile"]["grade_level"]
        learning_style = learning_context["student_profile"]["learning_style"]
        
        # Adapt content to grade level
        if grade_level in ["K", "1", "2"]:
            complexity = "very_simple"
            font_size = 64
        elif grade_level in ["3", "4", "5"]:
            complexity = "simple"
            font_size = 48
        else:
            complexity = "moderate"
            font_size = 36
        
        # Adapt to learning style
        animations = ["Write", "FadeIn"] if learning_style == "auditory" else ["Create", "Transform"]
        colors = ["BLUE", "GREEN", "YELLOW"] if learning_style == "visual" else ["WHITE", "LIGHT_BLUE"]
        
        script = f'''from manim import *

class ExplanationScene(Scene):
    def construct(self):
        # Enhanced title with personalization
        title = Text("{topic}", font_size={font_size}, color={colors[0]}, weight=BOLD)
        subtitle = Text("Personalized Learning", font_size={font_size//2}, color={colors[1]})
        subtitle.next_to(title, DOWN, buff=0.5)
        
        # Grade-appropriate introduction
        self.play({animations[0]}(title), run_time=2)
        self.play({animations[0]}(subtitle), run_time=1.5)
        self.wait(2)
        
        # Clear and transition
        self.play(FadeOut(title), FadeOut(subtitle))
        
        # Main learning content adapted to style
        if "{learning_style}" == "visual":
            content = Text("Let's visualize {topic}!", font_size={font_size-8}, color={colors[0]})
            diagram = Circle(radius=2, color={colors[1]})
            diagram.next_to(content, DOWN, buff=1)
            
            self.play({animations[0]}(content))
            self.play(Create(diagram))
            self.wait(3)
            
        elif "{learning_style}" == "kinesthetic":
            content = Text("Let's explore {topic} step by step!", font_size={font_size-8}, color={colors[0]})
            steps = VGroup()
            for i in range(3):
                step = Text(f"Step {{i+1}}: Learn about {topic}", font_size={font_size-16}, color={colors[1]})
                step.move_to(UP * (1-i) * 0.8)
                steps.add(step)
            
            self.play({animations[0]}(content))
            self.wait(1)
            self.play(FadeOut(content))
            
            for step in steps:
                self.play({animations[0]}(step), run_time=1.5)
                self.wait(1)
        
        else:  # auditory or mixed
            content = Text("Understanding {topic} is important\\nfor Grade {grade_level} students", 
                         font_size={font_size-12}, color={colors[0]})
            explanation = Text("This concept builds on what you already know\\nand prepares you for future learning", 
                             font_size={font_size-16}, color={colors[1]})
            explanation.next_to(content, DOWN, buff=1)
            
            self.play({animations[0]}(content))
            self.wait(2)
            self.play({animations[0]}(explanation))
            self.wait(3)
        
        # Personalized encouragement
        encouragement = Text("Great job learning about {topic}!\\nYou're making excellent progress!", 
                           font_size={font_size-8}, color=GREEN)
        
        self.play(FadeOut(*self.mobjects))
        self.play({animations[0]}(encouragement))
        self.wait(3)
        
        # Final fade
        self.play(FadeOut(encouragement))'''
        
        return {
            "script": script,
            "metadata": {
                "complexity": complexity,
                "learning_style_adapted": learning_style,
                "grade_appropriate": True,
                "personalization_level": "high",
                "concepts_covered": [topic],
                "interactive_elements": ["step_by_step"] if learning_style == "kinesthetic" else []
            }
        }
    
    async def _analyze_script_metadata(self, script: str, learning_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze generated script to extract metadata"""
        
        metadata = {
            "script_length": len(script),
            "animation_count": script.count("self.play("),
            "wait_count": script.count("self.wait("),
            "text_elements": script.count("Text(") + script.count("MathTex("),
            "visual_elements": script.count("Circle(") + script.count("Square(") + script.count("Rectangle("),
            "complexity_score": self._calculate_complexity_score(script),
            "concepts_covered": self._extract_concepts_from_script(script),
            "interactive_points": self._identify_interactive_points(script),
            "estimated_duration": self._estimate_video_duration(script)
        }
        
        return metadata
    
    def _calculate_complexity_score(self, script: str) -> float:
        """Calculate complexity score based on script content"""
        
        complexity_indicators = {
            "Transform(": 0.3,
            "MathTex(": 0.2,
            "VGroup(": 0.2,
            "for " : 0.1,
            "if ": 0.1,
            "def ": 0.3
        }
        
        score = 0.0
        for indicator, weight in complexity_indicators.items():
            score += script.count(indicator) * weight
        
        return min(1.0, score)
    
    def _extract_concepts_from_script(self, script: str) -> List[str]:
        """Extract mathematical/educational concepts from script"""
        
        # This could be enhanced with NLP, for now use simple pattern matching
        concepts = []
        
        import re
        
        # Look for mathematical terms in comments or text
        math_terms = re.findall(r'#.*?(equation|formula|theorem|proof|derivative|integral|function)', script, re.IGNORECASE)
        text_terms = re.findall(r'Text\("([^"]*)"', script)
        
        concepts.extend([term[1] if isinstance(term, tuple) else term for term in math_terms])
        concepts.extend([term for term in text_terms if len(term.split()) <= 3])  # Short phrases only
        
        return list(set(concepts))[:5]  # Return unique, limited list
    
    def _identify_interactive_points(self, script: str) -> List[str]:
        """Identify points where interactivity could be enhanced"""
        
        interactive_points = []
        
        if "self.wait(" in script:
            wait_count = script.count("self.wait(")
            interactive_points.extend([f"pause_point_{i+1}" for i in range(min(wait_count, 5))])
        
        if "Transform(" in script:
            interactive_points.append("transformation_sequence")
        
        if "for " in script:
            interactive_points.append("step_by_step_sequence")
        
        return interactive_points
    
    def _estimate_video_duration(self, script: str) -> int:
        """Estimate video duration based on script content"""
        
        # Base duration
        duration = 30  # 30 seconds base
        
        # Add time for animations
        duration += script.count("self.play(") * 3  # 3 seconds per animation
        
        # Add explicit wait times
        import re
        wait_matches = re.findall(r'self\.wait\((\d+(?:\.\d+)?)\)', script)
        for wait_time in wait_matches:
            duration += float(wait_time)
        
        # Add time for text content
        text_matches = re.findall(r'Text\("([^"]*)"', script)
        for text in text_matches:
            duration += len(text) * 0.05  # Reading time estimation
        
        return min(300, max(60, int(duration)))  # Between 1-5 minutes
    
    async def _create_fallback_variant(self, topic: str, timestamp: str) -> Dict[str, Any]:
        """Create fallback video variant when rendering fails"""
        
        return {
            "video_id": f"fallback_{timestamp}",
            "video_url": "/static/placeholder_video.mp4",
            "quality": VideoQuality.MEDIUM.value,
            "format": VideoFormat.MP4.value,
            "file_size_mb": 5.0,
            "duration_seconds": 120,
            "generation_time_seconds": 0.0,
            "fallback": True,
            "error": "Rendering failed, placeholder provided"
        }
    
    async def _get_video_duration(self, video_path: Path) -> Optional[float]:
        """Enhanced video duration detection"""
        try:
            # Try ffprobe first
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
            
        except Exception:
            # Fallback to file size estimation
            try:
                file_size_mb = video_path.stat().st_size / (1024 * 1024)
                # Rough estimation: 1 MB ≈ 20 seconds for educational video
                return file_size_mb * 20
            except Exception:
                return None
        
        return None
    
    def is_healthy(self) -> bool:
        """Enhanced health check for Phase 4 features"""
        try:
            # Check Manim availability
            result = subprocess.run(
                ["python", "-m", "manim", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return False
            
            # Check Gemini client
            if not self.gemini_client:
                return False
            
            # Check directories
            required_dirs = [self.videos_dir, self.temp_dir, self.thumbnails_dir, self.scripts_cache_dir]
            for directory in required_dirs:
                if not directory.exists():
                    return False
            
            return True
            
        except Exception:
            return False