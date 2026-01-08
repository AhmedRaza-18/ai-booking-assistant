"""
Voice Service
Handles phone calls via Twilio
"""
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.config.settings import settings
from typing import Optional


class VoiceService:
    """
    Manages voice calls through Twilio
    """
    
    def __init__(self):
        """
        Initialize Twilio client
        """
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.phone_number = settings.TWILIO_PHONE_NUMBER
            print("✅ Twilio Voice Service initialized")
        else:
            self.client = None
            self.phone_number = None
            print("⚠️  Twilio credentials not found - voice features disabled")
    
    
    def generate_greeting_response(self) -> str:
        """
        Generate TwiML for initial greeting
        TwiML = Twilio Markup Language (XML for voice)
        """
        response = VoiceResponse()
        
        # Gather speech input (listen for patient)
        gather = Gather(
            input='speech',
            action='/voice/process',
            method='POST',
            language='en-US',
            timeout=3,
            speech_timeout='auto'
        )
        
        # What AI says first
        gather.say(
            "Hello! Welcome to Bright Smile Dental Clinic. I'm Alex, your A I assistant. "
            "Are you a new patient, or have you visited us before?",
            voice='Polly.Joanna'  # Female voice
        )
        
        response.append(gather)
        
        # If no response, repeat
        response.say("I didn't hear anything. Please try again.")
        response.redirect('/voice/incoming')
        
        return str(response)
    
    
    def generate_response_with_text(self, ai_text: str, next_action: str = '/voice/process') -> str:
        """
        Generate TwiML with AI response
        
        Args:
            ai_text: What AI wants to say
            next_action: Where to send next response
        """
        response = VoiceResponse()
        
        # Gather next input
        gather = Gather(
            input='speech',
            action=next_action,
            method='POST',
            language='en-US',
            timeout=3,
            speech_timeout='auto'
        )
        
        # Say AI's response
        gather.say(ai_text, voice='Polly.Joanna')
        
        response.append(gather)
        
        # If no response
        response.say("I didn't catch that. Could you repeat?")
        response.redirect(next_action)
        
        return str(response)
    
    
    def generate_completion_response(self, final_message: str) -> str:
        """
        Generate final TwiML (end call)
        """
        response = VoiceResponse()
        response.say(final_message, voice='Polly.Joanna')
        response.say("Thank you for calling Bright Smile Dental. Goodbye!")
        response.hangup()
        
        return str(response)
    
    
    def make_outbound_call(
        self, 
        to_phone: str, 
        message: str
    ) -> Optional[str]:
        """
        Make an outbound call (for reminders)
        
        Args:
            to_phone: Patient's phone number
            message: What to say
        
        Returns:
            Call SID if successful
        """
        if not self.client:
            print("❌ Twilio not configured")
            return None
        
        try:
            # Create TwiML for message
            response = VoiceResponse()
            response.say(message, voice='Polly.Joanna')
            response.hangup()
            
            call = self.client.calls.create(
                twiml=str(response),
                to=to_phone,
                from_=self.phone_number
            )
            
            print(f"✅ Call initiated: {call.sid}")
            return call.sid
        
        except Exception as e:
            print(f"❌ Call failed: {e}")
            return None


# Singleton instance
voice_service = VoiceService()