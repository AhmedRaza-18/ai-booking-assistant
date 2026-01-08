"""
SMS Service
Handles sending SMS notifications via Twilio
"""
from twilio.rest import Client
from app.config.settings import settings
from typing import Optional
from datetime import datetime


class SMSService:
    """
    Service for sending SMS notifications
    """
    
    def __init__(self):
        """Initialize Twilio client"""
        try:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
            print(f"✅ SMS Service initialized with {self.from_number}")
        except Exception as e:
            print(f"❌ SMS Service initialization failed: {e}")
            self.client = None
    
    
    def send_booking_confirmation(
        self,
        to_phone: str,
        name: str,
        service: str,
        date: str,
        time: str
    ) -> bool:
        """
        Send appointment confirmation SMS
        
        Args:
            to_phone: Patient's phone number (e.g., '+923001234567')
            name: Patient name
            service: Service type (e.g., 'Dental Cleaning')
            date: Appointment date (e.g., 'Monday, Jan 13')
            time: Appointment time (e.g., '9:00 AM')
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            print("❌ Twilio client not initialized")
            return False
        
        try:
            # Format phone number (ensure it has + prefix)
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            # Create message
            message_body = f"""✅ Appointment Confirmed!

Name: {name}
Service: {service}
Date: {date}
Time: {time}

Bright Smile Dental Clinic
📞 Call us: {self.from_number}
Reply CANCEL to cancel"""
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone
            )
            
            print(f"✅ SMS sent to {to_phone} | SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMS to {to_phone}: {e}")
            return False
    
    
    def send_emergency_alert(
        self,
        to_phone: str,
        name: str,
        message: str
    ) -> bool:
        """
        Send emergency alert SMS
        
        Args:
            to_phone: Staff phone number
            name: Patient name
            message: Emergency details
        
        Returns:
            True if sent successfully
        """
        if not self.client:
            return False
        
        try:
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            alert_body = f"""🚨 EMERGENCY ALERT

Patient: {name}
Details: {message}
Time: {datetime.now().strftime('%I:%M %p')}

IMMEDIATE ATTENTION REQUIRED"""
            
            message = self.client.messages.create(
                body=alert_body,
                from_=self.from_number,
                to=to_phone
            )
            
            print(f"🚨 Emergency alert sent | SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send emergency alert: {e}")
            return False
    
    
    def send_reminder(
        self,
        to_phone: str,
        name: str,
        service: str,
        date: str,
        time: str
    ) -> bool:
        """
        Send appointment reminder SMS (24 hours before)
        
        Args:
            to_phone: Patient's phone number
            name: Patient name
            service: Service type
            date: Appointment date
            time: Appointment time
        
        Returns:
            True if sent successfully
        """
        if not self.client:
            return False
        
        try:
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            reminder_body = f"""⏰ Appointment Reminder

Hi {name}!

Your appointment is tomorrow:
Service: {service}
Date: {date}
Time: {time}

Bright Smile Dental Clinic
See you soon! 😊"""
            
            message = self.client.messages.create(
                body=reminder_body,
                from_=self.from_number,
                to=to_phone
            )
            
            print(f"⏰ Reminder sent to {to_phone} | SID: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send reminder: {e}")
            return False
    
    
    def send_custom_message(
        self,
        to_phone: str,
        message: str
    ) -> bool:
        """
        Send custom SMS message
        
        Args:
            to_phone: Recipient phone number
            message: Message text
        
        Returns:
            True if sent successfully
        """
        if not self.client:
            return False
        
        try:
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone
            
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            print(f"📱 Custom SMS sent to {to_phone} | SID: {msg.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send custom SMS: {e}")
            return False


# Create singleton instance
sms_service = SMSService()