# api/dependencies.py
from services.script_generator import ScriptGenerator
from services.animation_blueprint import AnimationBlueprint
from services.video_renderer import VideoRenderer
from services.tts_generator import TTSGenerator

_script_generator = None
_animation_blueprint = None
_video_renderer = None
_tts_generator = None

def get_script_generator(llm_provider: str = "mistral") -> ScriptGenerator:
    global _script_generator
    if _script_generator is None:
        _script_generator = ScriptGenerator(llm_provider)
    return _script_generator

def get_animation_blueprint(llm_provider: str = "mistral") -> AnimationBlueprint:
    global _animation_blueprint
    if _animation_blueprint is None:
        _animation_blueprint = AnimationBlueprint(llm_provider)
    return _animation_blueprint

def get_video_renderer() -> VideoRenderer:
    global _video_renderer
    if _video_renderer is None:
        _video_renderer = VideoRenderer()
    return _video_renderer

def get_tts_generator() -> TTSGenerator:
    global _tts_generator
    if _tts_generator is None:
        _tts_generator = TTSGenerator()
    return _tts_generator
