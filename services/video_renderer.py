
import logging
import os
from pathlib import Path
from datetime import datetime
from config import settings
try:
    # MoviePy 2.x+ uses this import path
    from moviepy import ColorClip, TextClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    # Fallback for older MoviePy 1.x
    from moviepy.editor import ColorClip, TextClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

logger = logging.getLogger(__name__)

class VideoRenderer:
    def __init__(self):
        self.output_dir = Path(settings.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, blueprint: dict, script_data: dict, audio_path: str = None) -> str:
        try:
            logger.info("Starting video rendering with MoviePy")
            
            topic = script_data.get('topic', 'video')
            safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_topic = safe_topic.replace(' ', '_')
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_filename = f"{safe_topic}_{timestamp}.mp4"
            video_path = self.output_dir / video_filename
            
            # Create video clips from script scenes
            scenes = script_data.get('scenes', [])
            clips = []
            
            # Default settings
            width, height = 1280, 720
            bg_color = (10, 10, 30) # Dark blue/black
            text_color = 'white'
            font_size = 50
            
            for i, scene in enumerate(scenes):
                duration = scene.get('duration', 5)
                text = scene.get('narration_text', '')
                
                # Create background
                bg_clip = ColorClip(size=(width, height), color=bg_color).set_duration(duration)
                
                # Create text
                # Note: moviepy requires ImageMagick for TextClip, falling back to basic if not present might be needed
                # For this prototype we assume a simple TextClip works or we handle error
                try:
                    txt_clip = TextClip(text, fontsize=font_size, color=text_color, size=(width-100, None), method='caption')
                    txt_clip = txt_clip.set_position('center').set_duration(duration)
                    
                    video = CompositeVideoClip([bg_clip, txt_clip])
                except Exception as e:
                    logger.warning(f"TextClip failed (likely ImageMagick missing): {e}")
                    # Fallback to just color clip if text fails
                    video = bg_clip
                
                clips.append(video)
            
            if not clips:
                # specific fallback if no scenes
                clips.append(ColorClip(size=(width, height), color=bg_color).set_duration(5))
                
            final_video = concatenate_videoclips(clips)
            
            # Add audio if available
            if audio_path and os.path.exists(audio_path):
                try:
                    audio = AudioFileClip(audio_path)
                    # Loop or cut audio to match video? Or extend video?
                    # Usually audio drives video, but here we used scene duration
                    # Let's trim audio to video length or vice versa
                    final_video = final_video.set_audio(audio)
                except Exception as e:
                    logger.error(f"Failed to attach audio: {e}")
            
            # Write file
            logger.info(f"Writing video file to {video_path}")
            final_video.write_videofile(
                str(video_path), 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                logger=None # Silence moviepy logger
            )
            
            logger.info(f"Video rendered successfully: {video_path}")
            return str(video_path)
            
        except Exception as e:
            logger.error(f"Video rendering failed: {str(e)}", exc_info=True)
            # Create empty placeholder as last resort so workflow doesn't crash completely?
            # No, better to raise error so user knows
            raise
