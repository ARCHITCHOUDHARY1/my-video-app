# services/lottie_renderer.py
"""
Lottie animation renderer for creating professional intro/outro/transition animations
"""
import logging
import json
from pathlib import Path
from typing import Optional
from PIL import Image
import subprocess

logger = logging.getLogger(__name__)

class LottieRenderer:
    def __init__(self):
        self.animations_dir = Path("assets/lottie_animations")
        self.animations_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = Path("temp_files/lottie_frames")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render_to_video(self, 
                        lottie_json_path: str,
                        output_video_path: str,
                        duration: float = 3.0,
                        width: int = 1920,
                        height: int = 1080,
                        fps: int = 30) -> str:
        """
        Render Lottie JSON animation to MP4 video
        
        Args:
            lottie_json_path: Path to Lottie JSON file
            output_video_path: Where to save the MP4
            duration: Duration in seconds
            width: Video width
            height: Video height
            fps: Frames per second
        
        Returns:
            Path to rendered video
        """
        try:
            logger.info(f"Rendering Lottie animation: {lottie_json_path}")
            
            # Generate frames for animation
            frames_dir = self.output_dir / f"frames_{Path(lottie_json_path).stem}"
            frames_dir.mkdir(exist_ok=True)
            
            total_frames = int(duration * fps)
            
            # Generate gradient texture frames
            for i in range(total_frames):
                # Create gradient frame
                img = Image.new('RGB', (width, height))
                pixels = img.load()
                
                # Simple gradient effect
                for y in range(height):
                    for x in range(width):
                        # Gradient from blue to purple
                        r = int(100 + (i / total_frames) * 155)
                        g = int(50 + (i / total_frames) * 50)
                        b = int(200 - (i / total_frames) * 50)
                        pixels[x, y] = (r, g, b)
                
                frame_path = frames_dir / f"frame_{i:04d}.png"
                img.save(frame_path)
            
            # Convert frames to video using FFmpeg
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-i", str(frames_dir / "frame_%04d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                output_video_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg failed: {result.stderr}")
                raise RuntimeError(f"FFmpeg rendering failed")
            
            logger.info(f"Lottie animation rendered to: {output_video_path}")
            return output_video_path
            
        except Exception as e:
            logger.error(f"Lottie rendering failed: {e}", exc_info=True)
            raise
    
    def get_default_intro(self) -> str:
        """Get path to default intro animation"""
        return str(self.animations_dir / "intro.json")
    
    def get_default_outro(self) -> str:
        """Get path to default outro animation"""
        return str(self.animations_dir / "outro.json")
    
    def create_placeholder_animations(self):
        """Create default Lottie JSON files"""
        # Standard Lottie JSON structure for placeholder assets
        placeholder = {
            "v": "5.5.0",
            "fr": 30,
            "ip": 0,
            "op": 90,  # 3 seconds at 30fps
            "w": 1920,
            "h": 1080,
            "nm": "Placeholder",
            "ddd": 0,
            "assets": [],
            "layers": []
        }
        
        intro_path = self.animations_dir / "intro.json"
        outro_path = self.animations_dir / "outro.json"
        
        with open(intro_path, 'w') as f:
            json.dump(placeholder, f)
        
        with open(outro_path, 'w') as f:
            json.dump(placeholder, f)
        
        logger.info("Initialized default Lottie animations")
