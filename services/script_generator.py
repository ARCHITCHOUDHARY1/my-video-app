# services/script_generator.py
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from config import settings

logger = logging.getLogger(__name__)

class ScriptGenerator:
    def __init__(self, llm_provider: str = "mistral"):
        self.llm_provider = llm_provider
        
        # Initialize LLM
        if llm_provider == "mistral":
            from langchain_mistralai import ChatMistralAI
            self.llm = ChatMistralAI(
                model="mistral-large-latest",
                temperature=settings.llm_temperature,
                api_key=settings.mistral_api_key
            )
            logger.info("Using Mistral AI API (primary)")
        elif llm_provider == "phi3":
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model="phi3:mini",
                base_url=settings.ollama_base_url,
                temperature=settings.llm_temperature
            )
            logger.info("Using Phi-3 Mini via LOCAL Ollama (free fallback)")
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Create LCEL chain with structured output
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a professional video script writer. Generate video scripts in valid JSON format only."),
            ("human", """Generate a video script for: {topic}

Style: {style}
Duration: {duration} seconds

Create scenes with:
1. Scene number
2. Duration (seconds)
3. Narration text
4. Concept explanation
5. Visual description

Return as JSON with this exact structure:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "duration": 15,
      "narration_text": "...",
      "concept": "...",
      "explanation": "..."
    }}
  ]
}}

Generate valid JSON only, no other text.""")
        ])
        
        # Build LCEL chain: prompt | llm | parser
        self.chain = self.prompt | self.llm | JsonOutputParser()
    
    def generate_script(self, topic: str, style: str, duration: int) -> dict:
        try:
            logger.info(f"Generating script for: {topic} using {self.llm_provider}")
            
            # Invoke LCEL chain
            script_data = self.chain.invoke({
                "topic": topic,
                "style": style,
                "duration": duration
            })
            
            # Add metadata
            script_data.update({
                'topic': topic,
                'style': style,
                'narration': " ".join([s.get('narration_text', '') for s in script_data.get('scenes', [])]),
                'voiceover_text': " ".join([s.get('narration_text', '') for s in script_data.get('scenes', [])]),
                'total_duration': sum([s.get('duration', 0) for s in script_data.get('scenes', [])])
            })
            
            logger.info(f"Script generated with {len(script_data.get('scenes', []))} scenes")
            return script_data
            
        except Exception as e:
            logger.error(f"Script generation failed with {self.llm_provider}: {str(e)}", exc_info=True)
            
            # Fallback to Phi-3
            if self.llm_provider == "mistral":
                logger.info("Attempting fallback to Phi-3 (local Ollama)...")
                try:
                    fallback_gen = ScriptGenerator("phi3")
                    return fallback_gen.generate_script(topic, style, duration)
                except Exception as fallback_error:
                    logger.error(f"Phi-3 fallback also failed: {str(fallback_error)}")
            
            raise
