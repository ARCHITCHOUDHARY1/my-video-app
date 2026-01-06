# api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

from models import WSMessage, WSProgressUpdate, WSError
from utils.logger_config import setup_logger

logger = setup_logger('websocket')

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.job_subscribers: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        
        # Remove from all job subscriptions
        for job_id in list(self.job_subscribers.keys()):
            if client_id in self.job_subscribers[job_id]:
                self.job_subscribers[job_id].remove(client_id)
        
        logger.info(f"Client disconnected: {client_id}")
    
    def subscribe_to_job(self, client_id: str, job_id: str):
        if job_id not in self.job_subscribers:
            self.job_subscribers[job_id] = set()
        self.job_subscribers[job_id].add(client_id)
        logger.info(f"Client {client_id} subscribed to job {job_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {str(e)}")
    
    async def send_progress(self, job_id: str, stage: str, progress: int, message: str):
        update = WSProgressUpdate(
            job_id=job_id,
            stage=stage,
            progress=progress,
            message=message
        )
        
        ws_message = WSMessage(
            type="progress",
            data=update.dict()
        )
        
        if job_id in self.job_subscribers:
            for client_id in self.job_subscribers[job_id]:
                await self.send_personal_message(ws_message.dict(), client_id)
        
        logger.info(f"Progress update sent for job {job_id}: {stage} - {progress}%")
    
    async def send_error(self, job_id: str, error: str):
        error_msg = WSError(error=error)
        
        ws_message = WSMessage(
            type="error",
            data=error_msg.dict()
        )
        
        if job_id in self.job_subscribers:
            for client_id in self.job_subscribers[job_id]:
                await self.send_personal_message(ws_message.dict(), client_id)
        
        logger.error(f"Error sent for job {job_id}: {error}")
    
    async def broadcast(self, message: dict):
        for client_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, client_id)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                job_id = data.get('job_id')
                if job_id:
                    manager.subscribe_to_job(client_id, job_id)
                    await manager.send_personal_message(
                        {
                            'type': 'subscribed',
                            'data': {'job_id': job_id}
                        },
                        client_id
                    )
            
            elif message_type == 'ping':
                await manager.send_personal_message(
                    {'type': 'pong', 'data': {}},
                    client_id
                )
            
            else:
                await manager.send_personal_message(
                    {
                        'type': 'error',
                        'data': {'error': 'Unknown message type'}
                    },
                    client_id
                )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        manager.disconnect(client_id)