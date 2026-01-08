from app.services.sms_service import sms_service

# Test SMS directly
result = sms_service.send_booking_confirmation(
    to_phone="+923124660742",
    name="Ahmed Khan",
    service="Dental Cleaning",
    date="Monday, Jan 13",
    time="9:00 AM"
)

print(f"SMS sent: {result}")