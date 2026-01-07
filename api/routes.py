# api/routes.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from models import (
    VideoGenerationRequest, VideoJobResponse, ScriptRequest, ScriptResponse,
    StyleAnalysisRequest, VideoStatus
)
from database import get_db, VideoJob
from workflows.video_workflow import VideoWorkflow
from api.websocket import manager
from utils.logger_config import setup_logger

logger = setup_logger('api')
router = APIRouter()

# Generate Script
@router.post("/script/generate", response_model=ScriptResponse)
async def generate_script(
    request: ScriptRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Script generation requested for: {request.topic}")
        
        workflow = VideoWorkflow(llm_provider=request.llm_provider.value)
        script = await workflow.generate_script_async(
            request.topic,
            request.style.value,
            request.duration
        )
        
        if not script:
            raise HTTPException(status_code=500, detail="Script generation failed")
        
        logger.info(f"Script generated: {len(script['scenes'])} scenes")
        return ScriptResponse(**script)
        
    except Exception as e:
        logger.error(f"Script generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Generate Video
@router.post("/video/generate", response_model=VideoJobResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Video generation requested: {request.topic}")
        
        job_id = str(uuid.uuid4())
        
        # Create job in database
        job = VideoJob(
            id=job_id,
            topic=request.topic,
            style=request.style_analysis.style.value,
            status=VideoStatus.PENDING,
            llm_provider=request.llm_provider.value
        )
        db.add(job)
        db.commit()
        
        # Start background task
        background_tasks.add_task(
            process_video_job,
            job_id,
            request.dict(),
            request.llm_provider.value
        )
        
        logger.info(f"Job created: {job_id}")
        
        return VideoJobResponse(
            job_id=job_id,
            status=VideoStatus.PENDING,
            topic=request.topic,
            style=request.style_analysis.style.value,
            message="Video generation started"
        )
        
    except Exception as e:
        logger.error(f"Video generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Get Job Status
@router.get("/video/status/{job_id}", response_model=VideoJobResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    try:
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return VideoJobResponse(
            job_id=job.id,
            status=job.status,
            topic=job.topic,
            style=job.style,
            progress=job.progress,
            message=job.message,
            video_url=job.video_path,
            report_url=job.report_url,
            created_at=job.created_at,
            completed_at=job.completed_at,
            error=job.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# List Jobs
@router.get("/video/jobs", response_model=List[VideoJobResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = 10,
    status: Optional[VideoStatus] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(VideoJob)
        
        if status:
            query = query.filter(VideoJob.status == status)
        
        jobs = query.order_by(VideoJob.created_at.desc()).offset(skip).limit(limit).all()
        
        return [
            VideoJobResponse(
                job_id=job.id,
                status=job.status,
                topic=job.topic,
                style=job.style,
                progress=job.progress,
                message=job.message,
                video_url=job.video_path,
                report_url=job.report_url,
                created_at=job.created_at,
                completed_at=job.completed_at,
                error=job.error
            )
            for job in jobs
        ]
        
    except Exception as e:
        logger.error(f"List jobs error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Download Video
@router.get("/video/download/{job_id}")
async def download_video(
    job_id: str,
    db: Session = Depends(get_db)
):
    try:
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != VideoStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Video not ready")
        
        if not job.video_path or not os.path.exists(job.video_path):
            raise HTTPException(status_code=404, detail="Video file not found")
        
        return FileResponse(
            job.video_path,
            media_type="video/mp4",
            filename=f"{job.topic.replace(' ', '_')}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Background task
async def process_video_job(job_id: str, request_data: dict, llm_provider: str):
    from database import SessionLocal
    
    db = SessionLocal()
    
    try:
        logger.info(f"Processing job: {job_id}")
        
        # Update status
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        job.status = VideoStatus.PROCESSING
        job.message = "Starting video generation"
        db.commit()
        
        # Send WebSocket update
        await manager.send_progress(job_id, "starting", 0, "Initializing")
        
        # Create workflow
        workflow = VideoWorkflow(llm_provider=llm_provider)
        
        # Generate video
        result = await workflow.process_full_workflow(
            job_id=job_id,
            topic=request_data['topic'],
            style_data=request_data['style_analysis'],
            db=db
        )
        
        if result and result.get('video_file'):
            job.status = VideoStatus.COMPLETED
            job.progress = 100
            job.message = "Video generation completed"
            job.video_path = result['video_file']
            job.report_url = result.get('report_url')
            job.completed_at = datetime.now()
            
            await manager.send_progress(job_id, "completed", 100, "Video ready")
        else:
            job.status = VideoStatus.FAILED
            job.error = "Video generation failed"
            job.message = "Failed to generate video"
            
            await manager.send_error(job_id, "Video generation failed")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Job processing error: {str(e)}", exc_info=True)
        
        job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
        job.status = VideoStatus.FAILED
        job.error = str(e)
        job.message = f"Error: {str(e)}"
        db.commit()
        
        await manager.send_error(job_id, str(e))
        
    finally:
        db.close()