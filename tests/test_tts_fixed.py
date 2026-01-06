# test_tts.py
"""
Test script to verify TTS providers are working correctly.
Tests: Sarvam AI, Hugging Face Piper, Coqui, and other providers.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.tts_generator import TTSGenerator
from config import settings

def test_provider(provider_name: str, text: str, language: str = "en"):
    """Test a specific TTS provider"""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()}")
    print(f"{'='*60}")
    print(f"Text: {text[:50]}...")
    print(f"Language: {language}")
    
    try:
        tts = TTSGenerator(provider=provider_name)
        audio_path = tts.generate_audio(text, language)
        
        if audio_path and Path(audio_path).exists():
            file_size = Path(audio_path).stat().st_size
            print(f"[OK] SUCCESS!")
            print(f"   Audio file: {audio_path}")
            print(f"   File size: {file_size:,} bytes")
            return True
        else:
            print(f"[FAIL] FAILED - No audio file generated")
            return False
            
    except Exception as e:
        print(f"[FAIL] ERROR: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("TTS PROVIDER TEST SUITE")
    print("="*60)
    
    # Test texts
    english_text = "Hello! This is a test of the text to speech system."
    hindi_text = "नमस्ते! यह टेक्स्ट टू स्पीच सिस्टम का परीक्षण है।"
    
    results = {}
    
    # Test 1: Hugging Face Piper
    print("\n\n[TEST 1] HUGGING FACE PIPER (English)")
    results['piper_en'] = test_provider('huggingface_piper', english_text, 'en')
    
    # Test 2: Hugging Face Piper (Hindi)
    print("\n\n[TEST 2] HUGGING FACE PIPER (Hindi)")
    results['piper_hi'] = test_provider('huggingface_piper', hindi_text, 'hi')
    
    # Test 3: Sarvam AI (Hindi)
    if settings.sarvam_api_key:
        print("\n\n[TEST 3] SARVAM AI (Hindi)")
        results['sarvam_hi'] = test_provider('sarvam', hindi_text, 'hi')
        
        print("\n\n[TEST 4] SARVAM AI (English)")
        results['sarvam_en'] = test_provider('sarvam', english_text, 'en')
    else:
        print("\n\n[WARN] SKIPPING SARVAM AI - No API key found")
        print("   Set SARVAM_API_KEY in .env to test")
    
    # Test 4: Coqui TTS (if available)
    print("\n\n[TEST 5] HUGGING FACE COQUI (English)")
    results['coqui_en'] = test_provider('huggingface_coqui', english_text, 'en')
    
    # Test 5: gTTS (fallback)
    print("\n\n[TEST 6] GOOGLE TTS (Hindi)")
    results['gtts_hi'] = test_provider('gtts', hindi_text, 'hi')
    
    # Test 6: Edge TTS
    print("\n\n[TEST 7] EDGE TTS (Hindi)")
    results['edge_hi'] = test_provider('edge_tts', hindi_text, 'hi')
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "[OK] PASS" if passed_test else "[FAIL] FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
    elif passed > 0:
        print(f"\n[WARN] SOME TESTS FAILED ({total - passed} failures)")
    else:
        print("\n[FAIL] ALL TESTS FAILED - Check your setup")
    
    # Configuration check
    print("\n" + "="*60)
    print("CONFIGURATION CHECK")
    print("="*60)
    print(f"TTS Provider: {settings.tts_provider}")
    print(f"TTS Language: {settings.tts_language}")
    print(f"Sarvam API Key: {'[OK] Set' if settings.sarvam_api_key else '[FAIL] Not set'}")
    print(f"Ollama URL: {settings.ollama_base_url}")

if __name__ == "__main__":
    main()
