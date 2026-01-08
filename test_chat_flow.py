"""
Test Chat Flow
Simulates a complete conversation
"""
import requests
import json
import sys
import os

# Add app to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.sheets_service import sheets_service

BASE_URL = "http://localhost:8000"

print("="*70)
print("💬 TESTING CHAT FLOW")
print("="*70)

# Start conversation
session_id = None

def send_message(message: str):
    """Helper function to send message"""
    global session_id
    
    payload = {
        "message": message
    }
    if session_id:
        payload["session_id"] = session_id
    
    response = requests.post(f"{BASE_URL}/chat/message", json=payload)
    data = response.json()
    
    # Update session_id
    if not session_id:
        session_id = data["session_id"]
    
    print(f"\n👤 Patient: {message}")
    print(f"🤖 AI: {data['response']}")
    print(f"📊 State: {data['state']}")
    print(f"✅ Complete: {data['is_complete']}")
    if data['missing_fields']:
        print(f"❓ Missing: {', '.join(data['missing_fields'])}")
    
    return data

# Simulate complete conversation
print("\n" + "="*70)
print("SIMULATING PATIENT CONVERSATION")
print("="*70)

# Turn 1: Initial greeting
send_message("Hi, I need help")

# Turn 2: New patient
send_message("I'm a new patient")

# Turn 3: Service
send_message("I need a teeth cleaning")

# Turn 4: Timeline
send_message("I'd like to come in this week")

# Turn 5: Name
send_message("My name is John Smith")

# Turn 6: Phone
send_message("555-123-4567")

# Turn 7: DOB
send_message("03/15/1990")

# Turn 8: Insurance
send_message("I have Blue Cross")

# Turn 9: Service reason (AI asked again)
send_message("Just a routine cleaning")

# Turn 10: Preferred time
send_message("Wednesday morning")

# Turn 11: Confirm booking
send_message("Yes, Wednesday at 10 AM works perfectly")

# Turn 12: Final confirmation
send_message("Yes, that's all correct")

# Turn 13: Confirm booking (should trigger logging)
send_message("Yes, please book it")

print("\n" + "="*70)
print("✅ CHAT FLOW TEST COMPLETE")
print(f"📝 Session ID: {session_id}")
print("="*70)

# Verify booking was logged to Google Sheets
print("\n🔍 VERIFYING GOOGLE SHEETS LOGGING...")
try:
    # Get all values from sheet
    all_values = sheets_service.sheet.get_all_values()
    
    # Find the row with our session_id
    booking_found = False
    for row in all_values[1:]:  # Skip header
        if len(row) >= 9 and row[8] == session_id:  # Column I is session_id
            print("✅ Booking found in Google Sheets!")
            print(f"   📅 Timestamp: {row[0]}")
            print(f"   👤 Name: {row[1]}")
            print(f"   📞 Phone: {row[2]}")
            print(f"   🦷 Service: {row[3]}")
            print(f"   📆 Date: {row[4]}")
            print(f"   🕐 Time: {row[5]}")
            print(f"   👨‍⚕️ Doctor: {row[6]}")
            print(f"   📊 Status: {row[7]}")
            print(f"   🔗 Session: {row[8]}")
            booking_found = True
            break
    
    if not booking_found:
        print("❌ Booking not found in Google Sheets!")
        print(f"   Expected session_id: {session_id}")
        print(f"   Total rows in sheet: {len(all_values)}")
        
except Exception as e:
    print(f"❌ Error checking Google Sheets: {e}")

print("\n" + "="*70)
print("🏁 TEST VERIFICATION COMPLETE")
print("="*70)