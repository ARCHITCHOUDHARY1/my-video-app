# workflows/workflow_nodes.py

import logging
from typing import Dict, Any
from services.script_generator import ScriptGenerator
from services.animation_blueprint import AnimationBlueprint
from services.video_renderer import VideoRenderer
from services.tts_generator import TTSGenerator
from services.ffmpeg_composer import FFmpegComposer
from utils.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

def script_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Script node: Generating script for {state['topic']}")
    
    generator = ScriptGenerator(state['llm_provider'])
    script_data = generator.generate_script(
        state['topic'],
        state['style_data']['style'],
        120  # duration
    )
    
    return {
        **state,
        "script_data": script_data,
        "progress": 25,
        "current_stage": "script_completed"
    }

def blueprint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Blueprint node: Creating animation blueprint")
    
    generator = AnimationBlueprint(state['llm_provider'])
    blueprint = generator.create_blueprint(
        state['script_data'],
        state['style_data']
    )
    
    return {
        **state,
        "blueprint": blueprint,
        "progress": 50,
        "current_stage": "blueprint_completed"
    }

def tts_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("TTS node: Generating voiceover")
    
    audio_path = None
    try:
        tts = TTSGenerator()
        voiceover_text = state['script_data'].get('voiceover_text', '')
        
        if voiceover_text:
            language = tts.detect_language(voiceover_text)
            audio_path = tts.generate_audio(voiceover_text, language)
            logger.info(f"Audio generated: {audio_path}")
    except Exception as e:
        logger.warning(f"TTS failed (optional): {e}")
    
    return {
        **state,
        "audio_path": audio_path,
        "progress": 70,
        "current_stage": "audio_completed"
    }

def render_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Render node: Creating video with hybrid renderer")
    
    from services.hybrid_video_renderer import HybridVideoRenderer
    
    renderer = HybridVideoRenderer()
    video_path = renderer.render(
        state['blueprint'],
        state['script_data'],
        state.get('audio_path')
    )
    
    return {
        **state,
        "video_path": video_path,
        "progress": 85,
        "current_stage": "video_completed"
    }

def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("Report node: Creating report")
    
    reporter = ReportGenerator()
    report_data = {
        'topic': state['topic'],
        'style': state['style_data']['style'],
        'status': 'COMPLETED',
        'video_path': str(state['video_path']),
        'script_data': str(state['script_data']),
        'blueprint_data': str(state['blueprint'])
    }
    
    report_url = reporter.create_report(report_data)
    
    return {
        **state,
        "report_url": report_url,
        "progress": 100,
        "current_stage": "completed"
    }
