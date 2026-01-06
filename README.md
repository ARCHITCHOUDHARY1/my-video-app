# README.md
# Video Synthesis System - 100% Free Option

AI-powered video generation with **near-zero cost**.

## 🎯 Stack

**LLM**: Mistral API ($0.01) → Phi-3 LOCAL (FREE)  
**TTS**: Piper → Coqui → Bark → Sarvam → gTTS → Edge (ALL FREE)  
**Cost**: **$0.01/video** or **$0.00** with Phi-3 only

## ⚡ Quick Start

```bash
# 1. Install Ollama
ollama pull phi3:mini

# 2. Install packages
pip install -r requirements.txt

# 3. Configure
echo "MISTRAL_API_KEY=your-key" > .env

# 4. Run
python main.py
```

Visit: http://localhost:8000/docs

## 🎤 TTS Options (100% FREE)

| Provider | Quality | Speed | Cost |
|----------|---------|-------|------|
| Piper | 7/10 | Fast | FREE |
| Coqui | 8.5/10 | Medium | FREE |
| Bark | 9/10 | Slow | FREE |
| Sarvam | 8/10 | Fast | FREE* |
| gTTS | 6/10 | Fast | FREE |
| Edge TTS | 8/10 | Fast | FREE |

*Free tier available

## 🔄 Complete Fallback Chain

```
LLM:
Mistral API → Phi-3 LOCAL

TTS:
Piper → Coqui → Bark → Sarvam → gTTS → Edge TTS
```

**No OpenAI needed anywhere!**

## 💰 Cost Options

### Cheap (Recommended)
```
LLM: Mistral API ($0.01)
TTS: Piper (FREE)
Total: $0.01/video
```

### Completely Free
```
LLM: Phi-3 LOCAL (FREE)
TTS: Piper (FREE)
Total: $0.00/video
```

## 📡 API Usage

```bash
curl -X POST "localhost:8000/api/v1/video/generate" \
  -d '{
    "topic": "AI Basics",
    "llm_provider": "mistral",
    "style_analysis": {
      "style": "2D explainer",
      "colors": "blue,white",
      "animation_speed": "medium",
      "text_style": "bold",
      "transitions": "fade"
    }
  }'
```

## ⚙️ Configuration

```env
# LLM
MISTRAL_API_KEY=your-key  # $0.01, or skip for 100% free
OLLAMA_MODEL=phi3:mini    # FREE fallback

# TTS (100% FREE, no API keys!)
TTS_PROVIDER=huggingface_piper
```

## ✅ Features

✅ Mistral AI ($0.01) or Phi-3 (FREE)  
✅ 6 free TTS providers  
✅ Auto fallback chain  
✅ Indian language support  
✅ No OpenAI needed  
✅ WebSocket progress  
✅ REST API  

## 🌍 Language Support

- English: Piper, Edge TTS, gTTS
- Hindi/Tamil/Telugu: Sarvam, Edge TTS
- Auto-detection: Built-in

## 📚 Docs

- `ollama_setup.md` - Ollama + Phi-3
- `tts_setup.md` - 100% free TTS
- `quick_start.md` - Quick reference

## 💡 Key Points

✅ **NO OpenAI** needed for TTS  
✅ **6 FREE TTS** options  
✅ **Automatic** fallback  
✅ **$0.01** with Mistral  
✅ **$0.00** with Phi-3 only  

Start generating videos for free! 🚀
