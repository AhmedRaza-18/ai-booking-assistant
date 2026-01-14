"""
Conversation Service
Manages multi-turn conversations with patients
Tracks conversation state and guides the flow
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import logging

from app.services.sheets_service import sheets_service

logger = logging.getLogger(__name__)

# TTL for session expiration
SESSION_TTL_SECONDS = 1800  # 30 minutes


class ConversationState(Enum):
    START = "start"
    GREETING = "greeting"
    IDENTIFY_PATIENT = "identify_patient"
    GET_SERVICE = "get_service"
    CHECK_URGENCY = "check_urgency"
    COLLECT_NAME = "collect_name"
    COLLECT_PHONE = "collect_phone"
    COLLECT_DOB = "collect_dob"
    COLLECT_INSURANCE = "collect_insurance"
    VERIFY_INFO = "verify_info"
    CHECK_AVAILABILITY = "check_availability"
    BOOK_APPOINTMENT = "book_appointment"
    CONFIRM_BOOKING = "confirm_booking"
    COMPLETED = "completed"
    EMERGENCY_TRANSFER = "emergency_transfer"


class ConversationSession:
    """
    Represents a single conversation session
    """

    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.state: ConversationState = ConversationState.START
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()

        self.data: Dict[str, Optional[str]] = {
            "name": None,
            "phone": None,
            "email": None,
            "dob": None,
            "service": None,
            "insurance": None,
            "patient_type": None,
            "urgency": None,
            "preferred_date": None,
            "preferred_time": None,
            "notes": None,
        }

        self.messages: List[Dict[str, str]] = []
        self.turn_count: int = 0

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        self.turn_count += 1
        self.updated_at = datetime.utcnow()

    def update_data(self, key: str, value: Any):
        if key in self.data and value:
            self.data[key] = value
            self.updated_at = datetime.utcnow()

    def get_missing_fields(self) -> List[str]:
        required = ["name", "phone", "dob", "service", "insurance"]
        return [f for f in required if not self.data.get(f)]

    def is_complete(self) -> bool:
        return not self.get_missing_fields()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "data": self.data,
            "messages": self.messages,
            "turn_count": self.turn_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ConversationManager:
    """
    Manages conversation flow and state transitions
    """

    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}

    # --- Session Management ---

    def get_or_create_session(self, session_id: str) -> ConversationSession:
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id)
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def persist_session(self, session: ConversationSession):
        """
        Persist session to DB or Sheets
        """
        try:
            from app.services.database_service import db_service  # your DB helper
            db_service.save_conversation(session.to_dict())
        except Exception as e:
            logger.error(f"Failed to persist session {session.session_id}: {e}")

    def cleanup_expired_sessions(self):
        """
        Remove sessions older than TTL
        """
        now = datetime.utcnow()
        expired = [
            sid for sid, s in self.sessions.items()
            if (now - s.updated_at).total_seconds() > SESSION_TTL_SECONDS
        ]
        for sid in expired:
            logger.info(f"Cleaning up expired session {sid}")
            del self.sessions[sid]

    # --- State Machine ---

    def determine_next_state(
        self,
        session: ConversationSession,
        user_message: str,
        ai_response: str,
    ) -> ConversationState:
        from app.services.qualification import lead_qualifier

        current_state = session.state
        text = user_message.lower()

        # START → GREETING
        if current_state == ConversationState.START:
            return ConversationState.GREETING

        # GREETING → IDENTIFY_PATIENT
        if current_state == ConversationState.GREETING:
            return ConversationState.IDENTIFY_PATIENT

        # Emergency check (global)
        urgency = lead_qualifier.extract_urgency_level(user_message)
        if urgency == "emergency":
            session.update_data("urgency", "emergency")

            sheets_service.log_booking({
                "caller_name": session.data.get("name", "Unknown"),
                "phone_number": session.data.get("phone", ""),
                "symptoms": f"EMERGENCY - {user_message[:100]}",
                "preferred_date": "",
                "preferred_time": "",
                "doctor": "",
                "status": "🚨 EMERGENCY",
                "session_id": session.session_id,
            })

            return ConversationState.EMERGENCY_TRANSFER

        # IDENTIFY_PATIENT → GET_SERVICE
        if current_state == ConversationState.IDENTIFY_PATIENT:
            patient_type = lead_qualifier.extract_patient_type(user_message)
            session.update_data("patient_type", patient_type)
            return ConversationState.GET_SERVICE

        # GET_SERVICE → CHECK_URGENCY
        if current_state == ConversationState.GET_SERVICE:
            service = lead_qualifier.extract_service_type(user_message)
            session.update_data("service", service)
            return ConversationState.CHECK_URGENCY

        # CHECK_URGENCY → COLLECT_NAME
        if current_state == ConversationState.CHECK_URGENCY:
            urgency = lead_qualifier.extract_urgency_level(user_message) or "routine"
            session.update_data("urgency", urgency)
            return ConversationState.COLLECT_NAME

        # COLLECT_NAME → COLLECT_PHONE
        if current_state == ConversationState.COLLECT_NAME:
            return ConversationState.COLLECT_PHONE

        # COLLECT_PHONE → COLLECT_DOB
        if current_state == ConversationState.COLLECT_PHONE:
            return ConversationState.COLLECT_DOB

        # COLLECT_DOB → COLLECT_INSURANCE
        if current_state == ConversationState.COLLECT_DOB:
            return ConversationState.COLLECT_INSURANCE

        # COLLECT_INSURANCE → VERIFY_INFO
        if current_state == ConversationState.COLLECT_INSURANCE:
            from app.services.qualification import lead_qualifier
            insurance = lead_qualifier.extract_insurance(user_message)
            session.update_data("insurance", insurance)
            return ConversationState.VERIFY_INFO

        # VERIFY_INFO → CHECK_AVAILABILITY
        if current_state == ConversationState.VERIFY_INFO:
            return ConversationState.CHECK_AVAILABILITY

        # CHECK_AVAILABILITY → BOOK_APPOINTMENT
        if current_state == ConversationState.CHECK_AVAILABILITY:
            return ConversationState.BOOK_APPOINTMENT

        # BOOK_APPOINTMENT → CONFIRM_BOOKING
        if current_state == ConversationState.BOOK_APPOINTMENT:
            return ConversationState.CONFIRM_BOOKING

        # CONFIRM_BOOKING → COMPLETED
        if current_state == ConversationState.CONFIRM_BOOKING:
            if any(word in text for word in ["yes", "confirm", "correct"]):
                return ConversationState.COMPLETED
            return ConversationState.CHECK_AVAILABILITY

        return current_state

    # --- AI Prompt for each state ---

    def get_state_prompt(
        self, state: ConversationState, session: ConversationSession
    ) -> str:

        prompts = {
            ConversationState.GREETING:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "Welcome to Bright Smile Dental Clinic. I'm Alex, your receptionist today. I'd be happy to help you schedule an appointment. How can I assist you today?" Do NOT ask about patient type or services.""",

            ConversationState.IDENTIFY_PATIENT:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "Are you a new patient or have you visited us before?" Do NOT ask about services or anything else.""",

            ConversationState.GET_SERVICE:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "What dental service do you need? (cleaning, checkup, pain, etc.)" Do NOT ask about urgency or anything else.""",

            ConversationState.CHECK_URGENCY:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "When would you like to be seen? (today, this week, next week, etc.)" Do NOT ask for name or anything else.""",

            ConversationState.COLLECT_NAME:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "What is your full name?" Do NOT ask for phone number or anything else.""",

            ConversationState.COLLECT_PHONE:
                f"""[CRITICAL MODE] You are a dental receptionist. Name is {session.data.get('name')}. Your response MUST be exactly: "What is your phone number?" Do NOT ask for DOB or anything else.""",

            ConversationState.COLLECT_DOB:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "What is your date of birth? (MM/DD/YYYY)" Do NOT ask about insurance or anything else.""",

            ConversationState.COLLECT_INSURANCE:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "Do you have dental insurance or will you pay cash?" Do NOT verify information or ask anything else.""",

            ConversationState.VERIFY_INFO:
                f"""[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly this confirmation:

Name: {session.data.get('name')}
Phone: {session.data.get('phone')}
DOB: {session.data.get('dob')}
Service: {session.data.get('service')}
Insurance: {session.data.get('insurance')}

"Is this information correct?"

Do NOT ask for availability or book anything.""",

            ConversationState.CHECK_AVAILABILITY:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "What date and time would you prefer for your appointment?" Do NOT book or confirm anything.""",

            ConversationState.BOOK_APPOINTMENT:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "I'll book your appointment now. Is that okay?" Do NOT provide next steps or confirm booking.""",

            ConversationState.CONFIRM_BOOKING:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "Your appointment has been booked successfully. We'll send you a confirmation SMS. Thank you for choosing Bright Smile Dental!" Do NOT ask additional questions.""",

            ConversationState.EMERGENCY_TRANSFER:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "This sounds like an emergency. I'm transferring you to our emergency line right now. Please hold." Do NOT ask questions.""",

            ConversationState.COMPLETED:
                """[CRITICAL MODE] You are a dental receptionist. Your response MUST be exactly: "Thank you for choosing Bright Smile Dental Clinic. We look forward to seeing you. Goodbye." Do NOT ask additional questions.""",
        }

        return prompts.get(state, "Continue the conversation.")


# --- Singleton instance ---
conversation_manager = ConversationManager()
