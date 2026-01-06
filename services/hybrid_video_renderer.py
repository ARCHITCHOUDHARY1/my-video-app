# services/hybrid_video_renderer.py
"""
Hybrid video renderer combining Lottie animations with MoviePy text overlays
"""
import logging
from pathlib import Path
import subprocess
from services.lottie_renderer import LottieRenderer
from services.video_renderer import VideoRenderer
from config import settings

logger = logging.getLogger(__name__)

class HybridVideoRenderer:
    def __init__(self):
        self.lottie = LottieRenderer()
        self.moviepy = VideoRenderer()
        self.temp_dir = Path("temp_files/hybrid")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, blueprint: dict, script_data: dict, audio_path: str = None) -> str:
        """
        Render video using hybrid approach:
        1. Lottie intro (3 sec)
        2. MoviePy content slides (dynamic)
        3. Lottie outro (3 sec)
        
        Args:
            blueprint: Animation blueprint data
            script_data: Script with scenes
            audio_path: Optional audio file
        
        Returns:
            Path to final rendered video
        """
        try:
            logger.info("Starting hybrid video rendering")
            
            # Ensure placeholder animations exist
            self.lottie.create_placeholder_animations()
            
            # 1. Render Lottie intro
            intro_path = str(self.temp_dir / "intro.mp4")
            logger.info("Rendering Lottie intro...")
            self.lottie.render_to_video(
                self.lottie.get_default_intro(),
                intro_path,
                duration=3.0
            )
            
            # 2. Render MoviePy content
            content_path = str(self.temp_dir / "content.mp4")
            logger.info("Rendering MoviePy content...")
            self.moviepy.render(blueprint, script_data, None)  # No audio yet
            
            # Rename to content_path
            import shutil
            latest_video = sorted(Path(settings.output_dir).glob("*.mp4"))[-1]
            shutil.copy(latest_video, content_path)
            
            # 3. Render Lottie outro
            outro_path = str(self.temp_dir / "outro.mp4")
            logger.info("Rendering Lottie outro...")
            self.lottie.render_to_video(
                self.lottie.get_default_outro(),
                outro_path,
                duration=3.0
            )
            
            # 4. Concatenate all parts
            final_path = str(Path(settings.output_dir) / f"hybrid_video_{Path(content_path).stem}.mp4")
            self._concatenate_videos([intro_path, content_path, outro_path], final_path)
            
            # 5. Add audio if provided
            if audio_path:
                logger.info("Adding audio to hybrid video...")
                final_with_audio = str(Path(settings.output_dir) / f"hybrid_final_{Path(content_path).stem}.mp4")
                self._add_audio(final_path, audio_path, final_with_audio)
                return final_with_audio
            
            logger.info(f"Hybrid video rendered: {final_path}")
            return final_path
            
        except Exception as e:
            logger.error(f"Hybrid rendering failed: {e}", exc_info=True)
            # Fallback to pure MoviePy
            logger.warning("Falling back to MoviePy-only rendering")
            return self.moviepy.render(blueprint, script_data, audio_path)
    
    def _concatenate_videos(self, video_paths: list, output_path: str):
        """Concatenate multiple videos using FFmpeg"""
        # Create concat file
        concat_file = self.temp_dir / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video in video_paths:
                f.write(f"file '{Path(video).absolute()}'\n")
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Concatenation failed: {result.stderr}")
            raise RuntimeError("Video concatenation failed")
        
        logger.info(f"Concatenated {len(video_paths)} videos")
    
    def _add_audio(self, video_path: str, audio_path: str, output_path: str):
        """Add audio track to video"""
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            "-shortest",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Audio addition failed: {result.stderr}")
            raise RuntimeError("Audio addition failed")
        
        logger.info("Audio added to video")
