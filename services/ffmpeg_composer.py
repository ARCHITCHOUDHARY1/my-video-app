# services/ffmpeg_composer.py
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class FFmpegComposer:
    def add_audio(self, video_path: str, audio_path: str) -> str:
        try:
            logger.info(f"Adding audio to video")
            
            output_path = str(Path(video_path).with_name(f"{Path(video_path).stem}_with_audio.mp4"))
            
            cmd = [
                "ffmpeg", "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Audio added: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg failed: {result.stderr}")
                return video_path
                
        except FileNotFoundError:
            logger.warning("FFmpeg not found, skipping audio merge")
            return video_path
        except Exception as e:
            logger.error(f"Audio merge failed: {str(e)}")
            return video_path
