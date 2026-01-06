# models.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class StyleType(str, Enum):
    EXPLAINER_2D = "2D explainer"
    LINE_BASED = "line-based animation"
    FLOWCHART = "flowchart + arrow animations"
    CHARACTER = "character-based"
    WHITEBOARD = "whiteboard/doodle"
    UI_WALKTHROUGH = "UI walkthrough"
    KINETIC_TYPOGRAPHY = "kinetic typography"
    INFOGRAPHIC = "infographic motion graphics"
    STORYTELLING = "storytelling scenes"

class AnimationSpeed(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"

class TextStyle(str, Enum):
    BOLD = "bold"
    LIGHT = "light"
    HANDWRITTEN = "handwritten"

class TransitionType(str, Enum):
    FADE = "fade"
    SLIDE = "slide"
    CUT = "cut"

class LLMProvider(str, Enum):
    MISTRAL = "mistral"
    PHI3 = "phi3"

class VideoStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Request Models

class StyleAnalysisRequest(BaseModel):
    style: StyleType
    colors: str = Field(..., min_length=1, description="Comma-separated colors")
    animation_speed: AnimationSpeed
    text_style: TextStyle
    transitions: TransitionType
    reference_video_url: Optional[str] = None
    
    @validator('colors')
    def validate_colors(cls, v):
        colors = [c.strip() for c in v.split(',')]
        if len(colors) < 1:
            raise ValueError('At least one color required')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "style": "2D explainer",
                "colors": "blue,white,green",
                "animation_speed": "medium",
                "text_style": "bold",
                "transitions": "fade",
                "reference_video_url": "https://youtube.com/watch?v=example"
            }
        }

class VideoGenerationRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=200)
    style_analysis: StyleAnalysisRequest
    llm_provider: LLMProvider = LLMProvider.MISTRAL
    include_voiceover: bool = True
    video_duration: Optional[int] = Field(120, ge=30, le=600, description="Duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "How Neural Networks Work",
                "style_analysis": {
                    "style": "flowchart + arrow animations",
                    "colors": "purple,cyan,white",
                    "animation_speed": "medium",
                    "text_style": "bold",
                    "transitions": "slide"
                },
                "llm_provider": "mistral",
                "include_voiceover": True,
                "video_duration": 120
            }
        }

class ScriptRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    style: StyleType
    duration: int = Field(120, ge=30, le=600)
    llm_provider: LLMProvider = LLMProvider.MISTRAL

# Response Models

class SceneModel(BaseModel):
    scene_number: int
    duration: int
    narration_text: str
    concept: str
    explanation: str

class ScriptResponse(BaseModel):
    topic: str
    style: str
    narration: str
    scenes: List[SceneModel]
    voiceover_text: str
    total_duration: int
    created_at: datetime = Field(default_factory=datetime.now)

class StoryboardFrame(BaseModel):
    scene: int
    description: str
    composition: str
    visual_elements: List[str]
    text_overlays: List[str]
    animation_movement: str

class AnimationElement(BaseModel):
    name: str
    element_type: str
    description: str
    color: str
    size: Optional[str] = None

class AnimationInstruction(BaseModel):
    scene: int
    entry_animation: str
    main_animation: str
    exit_animation: str
    duration: float

class TimingMarker(BaseModel):
    scene: int
    start: float
    end: float
    duration: float

class TransitionModel(BaseModel):
    from_scene: int
    to_scene: int
    transition_type: str
    duration: float

class AssetPrompt(BaseModel):
    element_name: str
    prompt: str
    asset_type: str

class BlueprintResponse(BaseModel):
    storyboard: List[StoryboardFrame]
    elements: List[AnimationElement]
    animation_instructions: List[AnimationInstruction]
    timing: List[TimingMarker]
    transitions: List[TransitionModel]
    asset_prompts: List[AssetPrompt]
    created_at: datetime = Field(default_factory=datetime.now)

class VideoJobResponse(BaseModel):
    job_id: str
    status: VideoStatus
    topic: str
    style: str
    progress: int = 0
    message: str = ""
    video_url: Optional[str] = None
    report_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    services: Dict[str, bool]

# WebSocket Models

class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class WSProgressUpdate(BaseModel):
    job_id: str
    stage: str
    progress: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class WSError(BaseModel):
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Database Models (SQLAlchemy)

from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class VideoJob(Base):
    __tablename__ = "video_jobs"
    
    id = Column(String, primary_key=True, index=True)
    topic = Column(String(200), nullable=False)
    style = Column(String(50), nullable=False)
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.PENDING)
    progress = Column(Integer, default=0)
    message = Column(Text, default="")
    
    script_data = Column(Text, nullable=True)
    blueprint_data = Column(Text, nullable=True)
    
    video_path = Column(String(500), nullable=True)
    report_url = Column(String(500), nullable=True)
    
    llm_provider = Column(String(20), default="mistral")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    error = Column(Text, nullable=True)

class StyleProfile(Base):
    __tablename__ = "style_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    style = Column(String(50), nullable=False)
    colors = Column(String(200), nullable=False)
    animation_speed = Column(String(20), nullable=False)
    text_style = Column(String(20), nullable=False)
    transitions = Column(String(20), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())