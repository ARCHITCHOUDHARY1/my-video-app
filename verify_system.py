"""
System Verification Script
Tests all components to identify what works and what's missing
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60 + "\n")
    
    tests = [
        ("FastAPI", "fastapi", "FastAPI"),
        ("Pydantic", "pydantic", "BaseModel"),
        ("SQLAlchemy", "sqlalchemy", "create_engine"),
        ("LangChain", "langchain", "__version__"),
        ("Mistral AI", "langchain_mistralai", "ChatMistralAI"),
        ("Models", "models", "VideoGenerationRequest"),
        ("Config", "config", "settings"),
        ("Database", "database", "get_db"),
        ("Script Generator", "services.script_generator", "ScriptGenerator"),
        ("Blueprint", "services.animation_blueprint", "AnimationBlueprint"),
        ("Video Renderer", "services.video_renderer", "VideoRenderer"),
        ("TTS Generator", "services.tts_generator", "TTSGenerator"),
        ("Report Generator", "utils.report_generator", "ReportGenerator"),
        ("Google Docs", "services.google_docs_service", "GoogleDocsService"),
    ]
    
    passed = 0
    failed = []
    
    for name, module, attr in tests:
        try:
            mod = __import__(module, fromlist=[attr])
            if hasattr(mod, attr):
                print(f"[OK] {name}")
                passed += 1
            else:
                print(f"[FAIL] {name}: Missing {attr}")
                failed.append(name)
        except Exception as e:
            print(f"[FAIL] {name}: {str(e)[:50]}")
            failed.append(name)
    
    print(f"\nResult: {passed}/{len(tests)} passed")
    return len(failed) == 0, failed

def test_env_config():
    """Test environment configuration"""
    print("\n" + "="*60)
    print("TESTING ENVIRONMENT CONFIGURATION")
    print("="*60 + "\n")
    
    from config import settings
    
    checks = [
        ("MISTRAL_API_KEY", settings.mistral_api_key, "Required for AI features"),
        ("Output Directory", settings.output_dir, "Where videos are saved"),
        ("Temp Directory", settings.temp_dir, "For temporary files"),
        ("credentials.json", os.path.exists("credentials.json"), "For Google Docs (optional)"),
    ]
    
    warnings = []
    
    for name, value, description in checks:
        if value:
            print(f"[OK] {name}: {description}")
        else:
            print(f"[WARN] {name}: {description}")
            warnings.append(name)
    
    return warnings

def test_directories():
    """Test if required directories exist"""
    print("\n" + "="*60)
    print("TESTING DIRECTORIES")
    print("="*60 + "\n")
    
    dirs = [
        "generated_videos",
        "analysis_reports",
        "temp_files",
        "logs",
        "services",
        "utils",
        "api",
        "workflows"
    ]
    
    for dir_name in dirs:
        exists = os.path.exists(dir_name)
        print(f"[{'OK' if exists else 'MISSING'}] {dir_name}")
    
    return True

def main():
    print("\n" + "="*70)
    print(" SYSTEM VERIFICATION REPORT")
    print("="*70)
    
    # Test 1: Imports
    imports_ok, failed_imports = test_imports()
    
    # Test 2: Configuration
    warnings = test_env_config()
    
    # Test 3: Directories
    test_directories()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60 + "\n")
    
    if imports_ok:
        print("[OK] All imports working")
    else:
        print(f"[FAIL] Failed imports: {', '.join(failed_imports)}")
    
    if warnings:
        print(f"\n[WARN] Configuration warnings:")
        for w in warnings:
            print(f"  - {w}")
    
    if not imports_ok or warnings:
        print("\nACTION REQUIRED:")
        if not imports_ok:
            print("  1. Run: pip install -r requirements.txt")
        if "MISTRAL_API_KEY" in warnings:
            print("  2. Set MISTRAL_API_KEY in .env file")
        if "credentials.json" in warnings:
            print("  3. Add credentials.json for Google Docs (optional)")
    
    print("\n" + "="*60)
    print("WHAT WILL NOT WORK:")
    print("="*60 + "\n")
    
    blockers = []
    if "MISTRAL_API_KEY" in warnings:
        blockers.append("- AI Script Generation (requires MISTRAL_API_KEY)")
        blockers.append("- AI Blueprint Generation (requires MISTRAL_API_KEY)")
    
    if "credentials.json" in warnings:
        blockers.append("- Google Docs report (will fallback to local files)")
    
    if not imports_ok and "Video Renderer" in failed_imports:
        blockers.append("- Video rendering (MoviePy import failed)")
    
    if blockers:
        for blocker in blockers:
            print(blocker)
    else:
        print("[OK] All features should work!")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
