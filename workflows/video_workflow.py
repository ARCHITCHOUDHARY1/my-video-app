# workflows/video_workflow.py

import logging
from datetime import datetime
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from workflows.workflow_state import WorkflowState
from workflows.workflow_nodes import (
    script_node,
    blueprint_node,
    tts_node,
    render_node,
    report_node
)
from api.websocket import manager
from models import VideoStatus

logger = logging.getLogger(__name__)

class VideoWorkflow:
    def __init__(self, llm_provider: str = "mistral"):
        self.llm_provider = llm_provider
        
        # Build LangGraph workflow
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("generate_script", script_node)
        workflow.add_node("create_blueprint", blueprint_node)
        workflow.add_node("generate_audio", tts_node)
        workflow.add_node("render_video", render_node)
        workflow.add_node("create_report", report_node)
        
        # Define edges (workflow sequence)
        workflow.set_entry_point("generate_script")
        workflow.add_edge("generate_script", "create_blueprint")
        workflow.add_edge("create_blueprint", "generate_audio")
        workflow.add_edge("generate_audio", "render_video")
        workflow.add_edge("render_video", "create_report")
        workflow.add_edge("create_report", END)
        
        # Compile graph
        self.graph = workflow.compile()
        logger.info("LangGraph workflow compiled successfully")
    
    async def generate_script_async(self, topic: str, style: str, duration: int) -> dict:
    
        try:
            from services.script_generator import ScriptGenerator
            gen = ScriptGenerator(self.llm_provider)
            return gen.generate_script(topic, style, duration)
        except Exception as e:
            logger.error(f"Script generation failed: {str(e)}")
            raise
    
    async def process_full_workflow(
        self,
        job_id: str,
        topic: str,
        style_data: dict,
        db: Session
    ) -> dict:
        try:
            logger.info(f"Starting LangGraph workflow for job {job_id}")
            
            from database import VideoJob
            job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
            
            # Prepare initial state
            initial_state = {
                "job_id": job_id,
                "topic": topic,
                "style_data": style_data,
                "llm_provider": self.llm_provider,
                "script_data": None,
                "blueprint": None,
                "audio_path": None,
                "video_path": None,
                "report_url": None,
                "progress": 0,
                "current_stage": "initializing",
                "error": None
            }
            
            # Execute LangGraph workflow
            await manager.send_progress(job_id, "workflow", 0, "Starting workflow")
            
            final_state = self.graph.invoke(initial_state)
            
            # Update database with results
            job.script_data = str(final_state.get('script_data'))
            job.blueprint_data = str(final_state.get('blueprint'))
            job.video_path = str(final_state.get('video_path'))
            job.report_url = final_state.get('report_url')
            job.progress = 100
            job.message = "Video and Report completed"
            job.status = VideoStatus.COMPLETED
            job.completed_at = datetime.now()
            db.commit()
            
            await manager.send_progress(job_id, "completed", 100, "Workflow completed")
            
            logger.info(f"LangGraph workflow completed for job {job_id}")
            
            return {
                'video_file': final_state.get('video_path'),
                'report_url': final_state.get('report_url'),
                'script': final_state.get('script_data'),
                'blueprint': final_state.get('blueprint')
            }
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}", exc_info=True)
            
            job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
            job.status = VideoStatus.FAILED
            job.error = str(e)
            db.commit()
            
            await manager.send_error(job_id, str(e))
            raise
