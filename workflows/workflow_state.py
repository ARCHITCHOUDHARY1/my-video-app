# workflows/workflow_state.py
"""
State schema for LangGraph video workflow
"""
from typing import TypedDict, Optional, List, Dict, Any

class WorkflowState(TypedDict):
    """State passed between workflow nodes"""
    # Input
    job_id: str
    topic: str
    style_data: Dict[str, Any]
    llm_provider: str
    
    # Generated data
    script_data: Optional[Dict[str, Any]]
    blueprint: Optional[Dict[str, Any]]
    audio_path: Optional[str]
    video_path: Optional[str]
    report_url: Optional[str]
    
    # Progress tracking
    progress: int
    current_stage: str
    error: Optional[str]
