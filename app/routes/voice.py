"""
Voice Routes
API endpoints for Twilio voice calls
"""
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from typing import Optional
import uuid
import logging

from app.services.voice_service import voice_service
from app.services.ai_service import ai_service
from app.services.conversation_service import conversation_manager
from app.services.database_service import db_service
from app.services.sms_service import sms_service
from app.services.sheets_service import sheets_service

router = APIRouter(prefix="/voice", tags=["voice"])
logger = logging.getLogger(__name__)


@router.post("/incoming", response_class=Response)
async def incoming_call(request: Request):
    """
    Handle incoming call (first interaction)
    """
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
    """
    session_id = CallSid or str(uuid.uuid4())
    session = conversation_manager.get_or_create_session(session_id)

    if not SpeechResult:
        twiml = voice_service.generate_response_with_text(
            "I didn't catch that. Could you please repeat?"
        )
        return Response(content=twiml, media_type="application/xml")

    # Add user message
    session.add_message("user", SpeechResult)

    # Build AI prompt
    state_prompt = conversation_manager.get_state_prompt(session.state, session)
    recent_messages = session.messages[-6:]
    ai_response = ai_service.chat(SpeechResult, recent_messages)
    session.add_message("assistant", ai_response)

    # Extract info from speech
    from app.routes.chat import _extract_information_from_message
    _extract_information_from_message(session, SpeechResult)

    # Update conversation state
    session.state = conversation_manager.determine_next_state(session, SpeechResult, ai_response)

    # ✅ Booking complete
    if session.is_complete():
        try:
            # 1. Save booking to database
            db_service.save_booking(
                session_id=session.session_id,
                booking_data={
                    "caller_name": session.data.get("name"),
                    "phone_number": session.data.get("phone"),
                    "service": session.data.get("service"),
                    "preferred_date": session.data.get("preferred_date"),
                    "preferred_time": session.data.get("preferred_time"),
                    "sms_sent": False,
                    "doctor": "TBD",
                    "status": "Confirmed",
                    "insurance": session.data.get("insurance")
                },
                source="voice"
            )

            # 2. Persist conversation in memory/db
            conversation_manager.persist_session(session)

            # 3. Log to Google Sheets
            sheets_service.log_booking(
                name=session.data.get("name"),
                phone=session.data.get("phone"),
                service=session.data.get("service"),
                source="voice"
            )

            # 4. Send SMS confirmation
            sms_service.send_booking_confirmation(
                to=session.data.get("phone"),
                name=session.data.get("name"),
                service=session.data.get("service")
            )

        except Exception as e:
            logger.error(f"Voice booking persistence failed: {e}")

        finally:
            # 5. Cleanup session to prevent memory leaks
            conversation_manager.delete_session(session_id)

        twiml = voice_service.generate_completion_response(
            "Perfect! Your appointment is booked. "
            "You’ll receive a confirmation message shortly. Goodbye!"
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
    return {
        "status": "Voice service not configured",
        "message": "Add Twilio credentials to .env"
    }
