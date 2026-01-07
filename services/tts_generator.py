# services/tts_generator.py
import logging
import os
from pathlib import Path
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class TTSGenerator:
    def __init__(self, provider: str = None):
        self.temp_dir = Path(settings.temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider or settings.tts_provider
        
        logger.info(f"TTS Generator initialized with provider: {self.provider}")
    
    def generate_audio(self, text: str, language: str = None) -> str:
        lang = language or settings.tts_language
        
        try:
            if self.provider == "huggingface_piper":
                return self._generate_piper(text, lang)
            elif self.provider == "huggingface_coqui":
                return self._generate_coqui(text, lang)
            elif self.provider == "bark":
                return self._generate_bark(text, lang)
            elif self.provider == "sarvam":
                return self._generate_sarvam(text, lang)
            elif self.provider == "gtts":
                return self._generate_gtts(text, lang)
            elif self.provider == "edge_tts":
                return self._generate_edge_tts(text, lang)
            else:
                logger.warning(f"Unknown provider {self.provider}, using Piper")
                return self._generate_piper(text, lang)
                
        except Exception as e:
            logger.error(f"TTS generation failed with {self.provider}: {str(e)}")
            return self._create_placeholder()
    
    def _generate_piper(self, text: str, language: str) -> str:
        
        try:
            logger.info("Generating audio with Piper TTS")
            
            import subprocess
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"piper_{timestamp}.wav"
            
            model_map = {
                "en": "en_US-lessac-medium",
                "hi": "hi_IN-medium",
                "ta": "ta_IN-medium",
                "te": "te_IN-medium"
            }
            
            model = model_map.get(language, "en_US-lessac-medium")
            
            cmd = [
                "piper",
                "--model", model,
                "--output_file", str(audio_path)
            ]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text[:5000])
            
            if process.returncode == 0 and audio_path.exists():
                logger.info(f"Piper TTS audio generated: {audio_path}")
                return str(audio_path)
            else:
                logger.warning(f"Piper failed: {stderr}")
                return self._generate_coqui(text, language)
                
        except FileNotFoundError:
            logger.warning("Piper not installed, falling back to Coqui")
            return self._generate_coqui(text, language)
        except Exception as e:
            logger.error(f"Piper TTS error: {str(e)}")
            return self._generate_coqui(text, language)
    
    def _generate_coqui(self, text: str, language: str) -> str:
        
        try:
            logger.info("Generating audio with Coqui TTS")
            
            from TTS.api import TTS
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"coqui_{timestamp}.wav"
            
            model_map = {
                "en": "tts_models/en/ljspeech/tacotron2-DDC",
                "hi": "tts_models/en/ljspeech/tacotron2-DDC",  # Fallback to EN
                "ta": "tts_models/en/ljspeech/tacotron2-DDC",
                "te": "tts_models/en/ljspeech/tacotron2-DDC"
            }
            
            model_name = model_map.get(language, model_map["en"])
            
            tts = TTS(model_name)
            tts.tts_to_file(
                text=text[:1000],
                file_path=str(audio_path)
            )
            
            logger.info(f"Coqui TTS audio generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Coqui TTS error: {str(e)}")
            return self._generate_bark(text, language)
    
    def _generate_bark(self, text: str, language: str) -> str:
        
        try:
            logger.info("Generating audio with Bark")
            
            from transformers import AutoProcessor, BarkModel
            import scipy
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"bark_{timestamp}.wav"
            
            processor = AutoProcessor.from_pretrained("suno/bark-small")
            model = BarkModel.from_pretrained("suno/bark-small")
            
            inputs = processor(text[:250], voice_preset="v2/en_speaker_6")
            audio_array = model.generate(**inputs)
            
            scipy.io.wavfile.write(
                str(audio_path),
                rate=model.generation_config.sample_rate,
                data=audio_array.cpu().numpy().squeeze()
            )
            
            logger.info(f"Bark audio generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Bark error: {str(e)}")
            return self._generate_sarvam(text, language)
    
    def _generate_sarvam(self, text: str, language: str) -> str:
        try:
            logger.info("Generating audio with Sarvam AI")
            
            import requests
            
            if not settings.sarvam_api_key:
                logger.warning("Sarvam API key not set, falling back to gTTS")
                return self._generate_gtts(text, language)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"sarvam_{timestamp}.wav"
            
            # Official Sarvam AI API
            url = "https://api.sarvam.ai/text-to-speech"
            
            headers = {
                "api-subscription-key": settings.sarvam_api_key,
                "content-type": "application/json"
            }
            
            # Language to Sarvam code mapping
            lang_map = {
                "hi": "hi-IN",
                "ta": "ta-IN",
                "te": "te-IN",
                "en": "en-IN",
                "bn": "bn-IN",
                "gu": "gu-IN",
                "kn": "kn-IN",
                "ml": "ml-IN",
                "mr": "mr-IN",
                "pa": "pa-IN"
            }
            
            # Voice/Speaker options: anushka, arvind, meera, etc.
            speaker_map = {
                "hi": "meera",      # Female Hindi
                "ta": "pallavi",    # Female Tamil
                "te": "shruti",     # Female Telugu
                "en": "anushka",    # Female English-Indian
            }
            
            payload = {
                "inputs": [text[:5000]],  # Sarvam uses "inputs" array
                "target_language_code": lang_map.get(language, "en-IN"),
                "speaker": speaker_map.get(language, "anushka"),
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.5,
                "speech_sample_rate": 22050,
                "enable_preprocessing": True,
                "model": "bulbul:v2"  # Latest Sarvam model
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                # Sarvam returns base64 encoded audio
                if 'audios' in result and len(result['audios']) > 0:
                    import base64
                    audio_b64 = result['audios'][0]
                    audio_bytes = base64.b64decode(audio_b64)
                    
                    with open(audio_path, 'wb') as f:
                        f.write(audio_bytes)
                    
                    logger.info(f"Sarvam AI audio generated: {audio_path}")
                    return str(audio_path)
                else:
                    logger.warning("Sarvam API returned no audio data")
                    return self._generate_gtts(text, language)
            else:
                logger.warning(f"Sarvam API failed: {response.status_code} - {response.text}")
                return self._generate_gtts(text, language)
                
        except Exception as e:
            logger.error(f"Sarvam AI error: {str(e)}")
            return self._generate_gtts(text, language)
    
    def _generate_gtts(self, text: str, language: str) -> str:
        try:
            logger.info("Generating audio with gTTS (Google TTS)")
            
            from gtts import gTTS
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"gtts_{timestamp}.mp3"
            
            lang_map = {
                "en": "en",
                "hi": "hi",
                "ta": "ta",
                "te": "te"
            }
            
            tts = gTTS(text=text[:5000], lang=lang_map.get(language, "en"))
            tts.save(str(audio_path))
            
            logger.info(f"gTTS audio generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"gTTS error: {str(e)}")
            return self._generate_edge_tts(text, language)
    
    def _generate_edge_tts(self, text: str, language: str) -> str:
        try:
            logger.info("Generating audio with Edge TTS")
            
            import edge_tts
            import asyncio
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audio_path = self.temp_dir / f"edge_{timestamp}.mp3"
            
            voice_map = {
                "en": "en-US-AriaNeural",
                "hi": "hi-IN-SwaraNeural",
                "ta": "ta-IN-PallaviNeural",
                "te": "te-IN-ShrutiNeural"
            }
            
            async def generate():
                communicate = edge_tts.Communicate(
                    text[:5000],
                    voice_map.get(language, "en-US-AriaNeural")
                )
                await communicate.save(str(audio_path))
            
            asyncio.run(generate())
            
            logger.info(f"Edge TTS audio generated: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Edge TTS error: {str(e)}")
            return self._create_placeholder()
    
    def _create_placeholder(self) -> str:
      
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        placeholder = self.temp_dir / f"placeholder_{timestamp}.mp3"
        placeholder.touch()
        
        logger.warning(f"Created placeholder audio: {placeholder}")
        return str(placeholder)
    
    def detect_language(self, text: str) -> str:
        
        if any('\u0900' <= char <= '\u097F' for char in text):
            return "hi"
        elif any('\u0B80' <= char <= '\u0BFF' for char in text):
            return "ta"
        elif any('\u0C00' <= char <= '\u0C7F' for char in text):
            return "te"
        else:
            return "en"
