# services/animation_blueprint.py
import logging
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import settings

logger = logging.getLogger(__name__)

class AnimationBlueprint:
    def __init__(self, llm_provider: str = "mistral"):
        self.llm_provider = llm_provider
        
        # Initialize LLM
        if llm_provider == "mistral":
            from langchain_mistralai import ChatMistralAI
            self.llm = ChatMistralAI(
                model="mistral-large-latest",
                temperature=0.6,
                api_key=settings.mistral_api_key
            )
            logger.info("Using Mistral AI API for blueprint")
        elif llm_provider == "phi3":
            from langchain_community.llms import Ollama
            self.llm = Ollama(
                model="phi3:mini",
                base_url=settings.ollama_base_url,
                temperature=0.6
            )
            logger.info("Using Phi-3 Mini via LOCAL Ollama for blueprint")
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
        
        # Create LCEL chain
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert animation director. Generate animation blueprints in valid JSON format only."),
            ("human", """Create animation blueprint for these scenes:

Scenes: {scenes}
Style: {style}
Colors: {colors}

Generate:
1. Storyboard frames
2. Animation elements
3. Animation instructions
4. Timing markers
5. Transitions

Return valid JSON with this structure:
{{
  "storyboard": [...],
  "elements": [...],
  "animation_instructions": [...],
  "timing": [...],
  "transitions": [...],
  "asset_prompts": [...]
}}

Return only valid JSON, no other text.""")
        ])
        
        self.chain = self.prompt | self.llm | JsonOutputParser()
    
    def create_blueprint(self, script_data: dict, style_data: dict) -> dict:
        try:
            logger.info(f"Creating animation blueprint using {self.llm_provider}")
            
            scenes = script_data.get('scenes', [])
            
            # Invoke LCEL chain
            blueprint = self.chain.invoke({
                "scenes": json.dumps(scenes, indent=2),
                "style": style_data.get('style'),
                "colors": style_data.get('colors')
            })
            
            logger.info("Blueprint created successfully")
            return blueprint
            
        except Exception as e:
            logger.error(f"Blueprint creation failed with {self.llm_provider}: {str(e)}", exc_info=True)
            
            # Fallback to Phi-3
            if self.llm_provider == "mistral":
                logger.info("Attempting fallback to Phi-3 (local Ollama) for blueprint...")
                try:
                    fallback_gen = AnimationBlueprint("phi3")
                    return fallback_gen.create_blueprint(script_data, style_data)
                except Exception as fallback_error:
                    logger.error(f"Phi-3 fallback also failed: {str(fallback_error)}")
            
            # Basic fallback structure
            return {
                "storyboard": [{"scene": i+1, "description": s.get('concept', '')} for i, s in enumerate(scenes)],
                "elements": [],
                "animation_instructions": [],
                "timing": [],
                "transitions": [],
                "asset_prompts": []
            }
