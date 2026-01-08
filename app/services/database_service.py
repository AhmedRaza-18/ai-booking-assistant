"""
Database Service
Handles saving and retrieving conversations and bookings
"""
from sqlalchemy.orm import Session
from app.models.database import Conversation, Booking, SessionLocal
from typing import Optional, List, Dict
import json
from datetime import datetime


class DatabaseService:
    """
    Service for database operations
    """
    
    def save_conversation(
        self,
        session_id: str,
        session_data: Dict,
        source: str = "chat"
    ) -> bool:
        """
        Save or update conversation in database
        
        Args:
            session_id: Unique session identifier
            session_data: Dictionary with conversation data
            source: Source of conversation (chat, voice, web)
        
        Returns:
            True if saved successfully
        """
        db = SessionLocal()
        try:
            # Check if conversation exists
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if conversation:
                # Update existing
                conversation.state = session_data.get('state', 'unknown')
                conversation.patient_name = session_data.get('data', {}).get('name')
                conversation.patient_phone = session_data.get('data', {}).get('phone')
                conversation.patient_email = session_data.get('data', {}).get('email')
                conversation.patient_dob = session_data.get('data', {}).get('dob')
                conversation.service_type = session_data.get('data', {}).get('service')
                conversation.insurance = session_data.get('data', {}).get('insurance')
                conversation.patient_type = session_data.get('data', {}).get('patient_type')
                conversation.urgency = session_data.get('data', {}).get('urgency')
                conversation.preferred_date = session_data.get('data', {}).get('preferred_date')
                conversation.preferred_time = session_data.get('data', {}).get('preferred_time')
                conversation.messages = json.dumps(session_data.get('messages', []))
                conversation.is_complete = session_data.get('state') == 'completed'
                conversation.updated_at = datetime.utcnow()
                
                if conversation.is_complete and not conversation.completed_at:
                    conversation.completed_at = datetime.utcnow()
            else:
                # Create new
                conversation = Conversation(
                    session_id=session_id,
                    state=session_data.get('state', 'start'),
                    patient_name=session_data.get('data', {}).get('name'),
                    patient_phone=session_data.get('data', {}).get('phone'),
                    patient_email=session_data.get('data', {}).get('email'),
                    patient_dob=session_data.get('data', {}).get('dob'),
                    service_type=session_data.get('data', {}).get('service'),
                    insurance=session_data.get('data', {}).get('insurance'),
                    patient_type=session_data.get('data', {}).get('patient_type'),
                    urgency=session_data.get('data', {}).get('urgency'),
                    preferred_date=session_data.get('data', {}).get('preferred_date'),
                    preferred_time=session_data.get('data', {}).get('preferred_time'),
                    messages=json.dumps(session_data.get('messages', [])),
                    is_complete=False,
                    source=source
                )
                db.add(conversation)
            
            db.commit()
            print(f"✅ Conversation {session_id} saved to database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save conversation: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    
    def get_conversation(self, session_id: str) -> Optional[Dict]:
        """
        Retrieve conversation from database
        
        Args:
            session_id: Session identifier
        
        Returns:
            Conversation data or None
        """
        db = SessionLocal()
        try:
            conversation = db.query(Conversation).filter(
                Conversation.session_id == session_id
            ).first()
            
            if not conversation:
                return None
            
            return {
                'session_id': conversation.session_id,
                'state': conversation.state,
                'data': {
                    'name': conversation.patient_name,
                    'phone': conversation.patient_phone,
                    'email': conversation.patient_email,
                    'dob': conversation.patient_dob,
                    'service': conversation.service_type,
                    'insurance': conversation.insurance,
                    'patient_type': conversation.patient_type,
                    'urgency': conversation.urgency,
                    'preferred_date': conversation.preferred_date,
                    'preferred_time': conversation.preferred_time
                },
                'messages': json.loads(conversation.messages) if conversation.messages else [],
                'is_complete': conversation.is_complete,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to get conversation: {e}")
            return None
        finally:
            db.close()
    
    
    def save_booking(
        self,
        session_id: str,
        booking_data: Dict
    ) -> bool:
        """
        Save confirmed booking to database
        
        Args:
            session_id: Session identifier
            booking_data: Booking details
        
        Returns:
            True if saved successfully
        """
        db = SessionLocal()
        try:
            booking = Booking(
                session_id=session_id,
                patient_name=booking_data.get('caller_name'),
                patient_phone=booking_data.get('phone_number'),
                patient_email=booking_data.get('email'),
                patient_dob=booking_data.get('dob'),
                service_type=booking_data.get('symptoms'),  # We use 'symptoms' for service
                appointment_date=booking_data.get('preferred_date'),
                appointment_time=booking_data.get('preferred_time'),
                doctor=booking_data.get('doctor', 'TBD'),
                status=booking_data.get('status', 'Pending'),
                insurance=booking_data.get('insurance'),
                sms_sent=booking_data.get('sms_sent', False)
            )
            
            db.add(booking)
            db.commit()
            print(f"✅ Booking saved to database for {booking_data.get('caller_name')}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save booking: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Get recent conversations
        
        Args:
            limit: Number of conversations to return
        
        Returns:
            List of conversation summaries
        """
        db = SessionLocal()
        try:
            conversations = db.query(Conversation).order_by(
                Conversation.updated_at.desc()
            ).limit(limit).all()
            
            return [{
                'session_id': c.session_id,
                'patient_name': c.patient_name,
                'patient_phone': c.patient_phone,
                'state': c.state,
                'is_complete': c.is_complete,
                'created_at': c.created_at.isoformat(),
                'updated_at': c.updated_at.isoformat()
            } for c in conversations]
            
        except Exception as e:
            print(f"❌ Failed to get recent conversations: {e}")
            return []
        finally:
            db.close()
    
    
    def get_bookings_by_date(self, date: str) -> List[Dict]:
        """
        Get bookings for a specific date
        
        Args:
            date: Date string
        
        Returns:
            List of bookings
        """
        db = SessionLocal()
        try:
            bookings = db.query(Booking).filter(
                Booking.appointment_date == date
            ).all()
            
            return [{
                'id': b.id,
                'patient_name': b.patient_name,
                'patient_phone': b.patient_phone,
                'service_type': b.service_type,
                'appointment_time': b.appointment_time,
                'doctor': b.doctor,
                'status': b.status
            } for b in bookings]
            
        except Exception as e:
            print(f"❌ Failed to get bookings: {e}")
            return []
        finally:
            db.close()


# Create singleton instance
db_service = DatabaseService()