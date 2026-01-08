"""
Voice Routes
API endpoints for Twilio voice calls
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from app.services.voice_service import voice_service
from app.services.ai_service import ai_service
from app.services.conversation_service import conversation_manager
from typing import Optional
import uuid


router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/incoming", response_class=Response)
async def incoming_call(request: Request):
    """
    Handle incoming call (first interaction)
    Twilio calls this when patient dials your number
    """
    # Generate greeting
    twiml = voice_service.generate_greeting_response()
    
    return Response(content=twiml, media_type="application/xml")


@router.post("/process", response_class=Response)
async def process_speech(
    request: Request,
    SpeechResult: Optional[str] = Form(None),
    CallSid: Optional[str] = Form(None)
):
    """
    Process patient speech and respond
    Twilio sends speech-to-text result here
    
    Args:
        SpeechResult: What patient said (Twilio converts speech→text)
        CallSid: Unique call identifier (use as session_id)
    """
    
    # Get or create conversation session
    session_id = CallSid or str(uuid.uuid4())
    session = conversation_manager.get_or_create_session(session_id)
    
    # If no speech detected
    if not SpeechResult:
        twiml = voice_service.generate_response_with_text(
            "I didn't catch that. Could you please repeat?"
        )
        return Response(content=twiml, media_type="application/xml")
    
    # Add patient message to conversation
    session.add_message("user", SpeechResult)
    
    # Get AI response
    state_prompt = conversation_manager.get_state_prompt(
        session.state, 
        session
    )
    
    # Enhanced prompt for voice (shorter responses)
    enhanced_prompt = f"""{ai_service.get_system_prompt()}

IMPORTANT: This is a VOICE call. Keep responses SHORT (1-2 sentences max).
Be conversational and natural. Don't list multiple things at once.

CURRENT STATE: {session.state.value}
TASK: {state_prompt}

COLLECTED INFO:
- Name: {session.data.get('name') or 'Not yet'}
- Phone: {session.data.get('phone') or 'Not yet'}
- Service: {session.data.get('service') or 'Not yet'}"""
    
    # Get AI response (use recent messages for context)
    recent_messages = session.messages[-6:]  # Last 6 messages
    ai_response = ai_service.chat(SpeechResult, recent_messages)
    
    # Add AI response to history
    session.add_message("assistant", ai_response)
    
    # Extract information
    from app.routes.chat import _extract_information_from_message
    _extract_information_from_message(session, SpeechResult)
    
    # Update state
    next_state = conversation_manager.determine_next_state(
        session,
        SpeechResult,
        ai_response
    )
    session.state = next_state
    
    # Check if booking is complete
    if session.is_complete():
        twiml = voice_service.generate_completion_response(
            f"Perfect! Your appointment is booked. "
            f"We'll send a confirmation to {session.data.get('phone')}."
        )
    else:
        twiml = voice_service.generate_response_with_text(ai_response)
    
    return Response(content=twiml, media_type="application/xml")


@router.get("/test")
async def test_voice():
    """
    Test endpoint to verify voice service is working
    """
    if voice_service.client:
        return {
            "status": "Voice service configured",
            "phone_number": voice_service.phone_number
        }
    else:
        return {
            "status": "Voice service not configured",
            "message": "Add Twilio credentials to .env"
        }