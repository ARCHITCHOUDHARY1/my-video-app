"""
End-to-end test for the complete workflow
Tests Part A and Part B integration
"""
import asyncio
import logging
from services.script_generator import ScriptGenerator
from services.animation_blueprint import AnimationBlueprint
from services.video_renderer import VideoRenderer
from services.tts_generator import TTSGenerator
from utils.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_workflow():
    print("\n" + "="*60)
    print("TESTING COMPLETE WORKFLOW")
    print("="*60 + "\n")
    
    # Configuration
    topic = "How Quantum Computing Works"
    style = "2D explainer"
    duration = 60
    
    print(f"âœ“ Configuration:")
    print(f"  Topic: {topic}")
    print(f"  Style: {style}")
    print(f"  Duration: {duration}s\n")
    
    # Step 1: Generate Script (Part B.2)
    print("STEP 1: Topic â†’ Script (AI Automatic)")
    print("-" * 60)
    try:
        script_gen = ScriptGenerator(llm_provider="mistral")
        script_data = script_gen.generate_script(topic, style, duration)
        print(f"âœ… Script generated with {len(script_data.get('scenes', []))} scenes")
        print(f"   Total duration: {script_data.get('total_duration', 0)}s\n")
    except Exception as e:
        print(f"âŒ Script generation failed: {e}\n")
        return False
    
    # Step 2: Create Blueprint (Part B.3)
    print("STEP 2: Script â†’ Animation Blueprint (AI Automatic)")
    print("-" * 60)
    try:
        blueprint_gen = AnimationBlueprint(llm_provider="mistral")
        style_data = {
            "style": style,
            "colors": "blue,white",
            "animation_speed": "medium",
            "text_style": "bold",
            "transitions": "fade"
        }
        blueprint = blueprint_gen.create_blueprint(script_data, style_data)
        print(f"âœ… Blueprint created")
        print(f"   Storyboard frames: {len(blueprint.get('storyboard', []))}")
        print(f"   Animation elements: {len(blueprint.get('elements', []))}\n")
    except Exception as e:
        print(f"âŒ Blueprint creation failed: {e}\n")
        return False
    
    # Step 3: Generate Audio (Optional TTS)
    print("STEP 3: Generate Voice-over (Optional TTS)")
    print("-" * 60)
    audio_path = None
    try:
        tts = TTSGenerator()
        voiceover_text = script_data.get('voiceover_text', '')
        if voiceover_text:
            language = tts.detect_language(voiceover_text)
            audio_path = tts.generate_audio(voiceover_text, language)
            print(f"âœ… Audio generated: {audio_path}\n")
        else:
            print("âš ï¸  No voiceover text, skipping TTS\n")
    except Exception as e:
        print(f"âš ï¸  TTS failed (optional): {e}\n")
    
    # Step 4: Render Video (Part B.4)
    print("STEP 4: Blueprint â†’ MP4 Video (AI Automatic)")
    print("-" * 60)
    try:
        renderer = VideoRenderer()
        video_path = renderer.render(blueprint, script_data, audio_path)
        print(f"âœ… Video rendered: {video_path}\n")
    except Exception as e:
        print(f"âŒ Video rendering failed: {e}\n")
        return False
    
    # Step 5: Generate Report (Part A Foundation)
    print("STEP 5: Create Research Report (Part A Foundation)")
    print("-" * 60)
    try:
        reporter = ReportGenerator()
        job_data = {
            'topic': topic,
            'style': style,
            'status': 'COMPLETED',
            'video_path': video_path,
            'script_data': str(script_data),
            'blueprint_data': str(blueprint)
        }
        report_url = reporter.create_report(job_data)
        
        if report_url and report_url.startswith('http'):
            print(f"âœ… Google Doc created: {report_url}\n")
        else:
            print(f"âœ… Local report created: {report_url}\n")
    except Exception as e:
        print(f"âš ï¸  Report generation failed (non-critical): {e}\n")
    
    print("="*60)
    print("âœ… WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"\nVideo File: {video_path}")
    if report_url:
        print(f"Report: {report_url}")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_workflow())
    exit(0 if result else 1)

