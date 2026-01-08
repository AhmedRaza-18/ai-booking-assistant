"""
Admin Routes
API endpoints for viewing conversations, bookings, and stats
"""
from fastapi import APIRouter, HTTPException
from app.services.database_service import db_service
from typing import List, Dict

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/conversations/recent")
async def get_recent_conversations(limit: int = 10):
    """
    Get recent conversations
    
    Example:
        GET /admin/conversations/recent?limit=20
    """
    conversations = db_service.get_recent_conversations(limit=limit)
    return {
        "count": len(conversations),
        "conversations": conversations
    }


@router.get("/conversation/{session_id}")
async def get_conversation_details(session_id: str):
    """
    Get detailed conversation by session ID
    
    Example:
        GET /admin/conversation/abc123
    """
    conversation = db_service.get_conversation(session_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("/bookings/date/{date}")
async def get_bookings_by_date(date: str):
    """
    Get bookings for a specific date
    
    Example:
        GET /admin/bookings/date/2026-01-15
    """
    bookings = db_service.get_bookings_by_date(date)
    return {
        "date": date,
        "count": len(bookings),
        "bookings": bookings
    }


@router.get("/stats")
async def get_stats():
    """
    Get system statistics
    
    Example:
        GET /admin/stats
    """
    # Get recent conversations to calculate stats
    recent = db_service.get_recent_conversations(limit=100)
    
    total_conversations = len(recent)
    completed = sum(1 for c in recent if c.get('is_complete'))
    in_progress = total_conversations - completed
    
    return {
        "total_conversations": total_conversations,
        "completed_bookings": completed,
        "in_progress": in_progress,
        "completion_rate": f"{(completed/total_conversations*100):.1f}%" if total_conversations > 0 else "0%"
    }