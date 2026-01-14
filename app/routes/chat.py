"""
Chat Routes
API endpoints for text-based conversations
"""
from app.services.database_service import db_service
from app.services.sms_service import sms_service
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.ai_service import ai_service
from app.services.conversation_service import conversation_manager, ConversationState
from app.services.qualification import lead_qualifier
from app.services.sheets_service import sheets_service
import uuid


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """
    Request model for chat messages
    """
    session_id: Optional[str] = None  # If not provided, creates new session
    message: str                       # User's message
    user_id: Optional[str] = None      # Optional user identifier


class ChatResponse(BaseModel):
    """
    Response model for chat
    """
    session_id: str
    response: str
    state: str
    data_collected: Dict
    missing_fields: List[str]
    is_complete: bool


@router.post("/message", response_model=ChatResponse)
async def send_message(chat_message: ChatMessage):
    """
    Send a message and get AI response
    Main chat endpoint
    
    Example:
        POST /chat/message
        {
            "session_id": "abc123",  # optional
            "message": "Hi, I need a cleaning"
        }
    """
    try:
        # Get or create session
        if not chat_message.session_id:
            session_id = str(uuid.uuid4())
        else:
            session_id = chat_message.session_id
        
        session = conversation_manager.get_or_create_session(session_id)
        
        # Add user message to history
        session.add_message("user", chat_message.message)
        
        # Get current state prompt
        state_prompt = conversation_manager.get_state_prompt(
            session.state, 
            session
        )
        
        # Create enhanced system prompt with state guidance
        enhanced_prompt = f"""You are Alex, a dental clinic receptionist.

CRITICAL INSTRUCTION: You are in state '{session.state.value}'.
Your ONLY task: {state_prompt}
Do NOT ask for other information. Ask ONE question only.

Current data: name={session.data.get('name')}, phone={session.data.get('phone')}, service={session.data.get('service')}

Be direct and wait for the answer."""
        
        print(f"🤖 AI PROMPT: {enhanced_prompt}")
        
        # Prepare conversation history for AI
        ai_messages = [
            {"role": "system", "content": enhanced_prompt}
        ]
        
        # Add recent conversation history (last 10 messages)
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        ai_messages.extend(recent_messages)
        
        # Get AI response
        ai_response = ai_service.chat(
            chat_message.message,
            recent_messages,
            system_prompt=enhanced_prompt
        )
        
        # Add AI response to history
        session.add_message("assistant", ai_response)
        
        # Store previous state for comparison
        previous_state = session.state
        
        # Determine next state FIRST
        next_state = conversation_manager.determine_next_state(
            session,
            chat_message.message,
            ai_response
        )
        
        print(f"🔄 State transition: {previous_state.value} -> {next_state.value}")
        
        # Update state BEFORE extraction (so extraction uses correct state)
        session.state = next_state
        
        # NOW extract information (with correct state)
        _extract_information_from_message(session, chat_message.message)
        
        # 🔥 LOG TO GOOGLE SHEETS when booking is ready
        should_log = False

        # Trigger 1: Reached COMPLETED state
        if next_state == ConversationState.COMPLETED and previous_state != ConversationState.COMPLETED:
            should_log = True
            print(f"🔥 Trigger 1: COMPLETED state reached")

        # Trigger 2: Reached CONFIRM_BOOKING (removed is_complete check)
        if next_state == ConversationState.CONFIRM_BOOKING and previous_state != ConversationState.CONFIRM_BOOKING:
            should_log = True
            print(f"🔥 Trigger 2: CONFIRM_BOOKING state reached")

        # Trigger 3: In BOOK_APPOINTMENT (removed is_complete check)
        if next_state == ConversationState.BOOK_APPOINTMENT and previous_state != ConversationState.BOOK_APPOINTMENT:
            should_log = True
            print(f"🔥 Trigger 3: BOOK_APPOINTMENT state reached")

        if should_log:
            booking_data = {
                'caller_name': session.data.get('name', 'Unknown'),
                'phone_number': session.data.get('phone', ''),
                'symptoms': session.data.get('service', ''),
                'preferred_date': session.data.get('preferred_date', 'TBD'),
                'preferred_time': session.data.get('preferred_time', 'TBD'),
                'doctor': 'To be assigned',
                'status': '✅ Completed',
                'session_id': session_id,
                'dob': session.data.get('dob', '')
            }
            
            print(f"🔥 TRIGGERING BOOKING LOG for {session.data.get('name')}")
            sheets_service.log_booking(booking_data)
            print(f"✅ Booking logged to Google Sheets for {session.data.get('name')}")
            
            # 🔥 SEND SMS CONFIRMATION
            phone = session.data.get('phone', '')
            if phone:
                sms_sent = sms_service.send_booking_confirmation(
                    to_phone=phone,
                    name=session.data.get('name', 'Patient'),
                    service=session.data.get('service', 'Appointment'),
                    date=session.data.get('preferred_date', 'TBD'),
                    time=session.data.get('preferred_time', 'TBD')
                )
                booking_data['sms_sent'] = sms_sent
            
            # 🔥 SAVE BOOKING TO DATABASE
            db_service.save_booking(
                session_id=session_id,
                booking_data=booking_data
            )
        
        # 🔥 SAVE CONVERSATION TO DATABASE (after every message)
        db_service.save_conversation(
            session_id=session_id,
            session_data=session.to_dict(),
            source="chat"
        )
        
        # Return response
        return ChatResponse(
            session_id=session_id,
            response=ai_response,
            state=session.state.value,
            data_collected=session.data,
            missing_fields=session.get_missing_fields(),
            is_complete=session.is_complete()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _extract_information_from_message(session, message: str):
    """
    Helper function to extract patient information from message
    Updates session data automatically
    """
    import re
    from app.services.conversation_service import ConversationState
    
    message_lower = message.lower().strip()
    current_state = session.state
    
    # FIRST: Try state-aware extraction for the current state
    if current_state == ConversationState.COLLECT_NAME:
        name = message.strip()
        name = re.sub(r'^(my name is |i am |this is |it\'s )', '', name, flags=re.IGNORECASE)
        name = re.sub(r'(here|speaking)$', '', name, flags=re.IGNORECASE)
        name = name.strip()
        if len(name.split()) >= 2 and not any(word in message_lower for word in ['phone', 'number', 'birth', 'insurance', 'cash']):
            session.update_data("name", name)
            return
    
    if current_state == ConversationState.COLLECT_PHONE:
        phone_patterns = [r'(\+\d{10,15})', r'(\d{10,15})', r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})']
        for pattern in phone_patterns:
            match = re.search(pattern, message)
            if match:
                phone = re.sub(r'[^\d+]', '', match.group(1))
                if len(phone) >= 10:
                    session.update_data("phone", phone)
                    return
    
    if current_state == ConversationState.COLLECT_DOB:
        dob_patterns = [r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', r'(\d{1,2}[/-]\d{1,2}[/-]\d{2})']
        for pattern in dob_patterns:
            match = re.search(pattern, message)
            if match:
                session.update_data("dob", match.group(1))
                return
    
    if current_state == ConversationState.COLLECT_INSURANCE:
        insurance = lead_qualifier.extract_insurance(message)
        if insurance:
            session.update_data("insurance", insurance)
            return
    
    # SECOND: If state-specific extraction failed, try general extraction from any message
    # This helps when AI doesn't follow prompts perfectly
    
    # Try to extract name from any message
    if not session.data.get("name"):
        name_match = re.search(r'(?:my name is|i am|this is|call me) ([A-Za-z\s]+?)(?:\s|$|and|\.|,)', message, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()
            if len(name.split()) >= 2:
                session.update_data("name", name)
    
    # Try to extract phone from any message  
    if not session.data.get("phone"):
        phone_match = re.search(r'(\+?\d{10,15})', message)
        if phone_match:
            phone = re.sub(r'[^\d+]', '', phone_match.group(1))
            if len(phone) >= 10:
                session.update_data("phone", phone)
    
    # Try to extract DOB from any message
    if not session.data.get("dob"):
        dob_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})', message)
        if dob_match:
            session.update_data("dob", dob_match.group(1))
    
    # Try to extract insurance from any message
    if not session.data.get("insurance"):
        insurance = lead_qualifier.extract_insurance(message)
        if insurance:
            session.update_data("insurance", insurance)
            return
    
    # GENERAL EXTRACTION - for any state
    
    # Extract service if not collected
    if not session.data.get("service"):
        service = lead_qualifier.extract_service_type(message)
        if service:
            session.update_data("service", service)
    
    # Extract patient type if not collected
    if not session.data.get("patient_type"):
        patient_type = lead_qualifier.extract_patient_type(message)
        if patient_type:
            session.update_data("patient_type", patient_type)
    
    # Extract urgency if not collected
    if not session.data.get("urgency"):
        urgency = lead_qualifier.extract_urgency_level(message)
        if urgency:
            session.update_data("urgency", urgency)
    
    # Extract date/time preferences
    if not session.data.get("preferred_date"):
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            if day in message_lower:
                session.update_data("preferred_date", day.capitalize())
                break
    
    if not session.data.get("preferred_time"):
        if "morning" in message_lower:
            session.update_data("preferred_time", "Morning")
        elif "afternoon" in message_lower:
            session.update_data("preferred_time", "Afternoon")
        elif "evening" in message_lower:
            session.update_data("preferred_time", "Evening")
        else:
            # Look for specific times
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',
                r'(\d{1,2}\s*(?:AM|PM|am|pm))'
            ]
            for pattern in time_patterns:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    session.update_data("preferred_time", match.group(1).upper())
                    break


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Get conversation session details
    
    Example:
        GET /chat/session/abc123
    """
    session = conversation_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete/end a conversation session
    
    Example:
        DELETE /chat/session/abc123
    """
    if session_id in conversation_manager.sessions:
        del conversation_manager.sessions[session_id]
        return {"message": "Session deleted", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")