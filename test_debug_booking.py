import requests
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = f"debug-{int(time.time())}"

messages = [
    "Hi, I need an appointment",
    "I am a new patient", 
    "I need a teeth cleaning",
    "Next week would be good",
    "My name is Test Ahmed raza",
    "My phone is 03124660742",
    "01/15/2003",
    "I will pay cash",
]

print("Testing step by step...\n")

for i, msg in enumerate(messages, 1):
    print(f"{i}. Sending: {msg}")
    resp = requests.post(
        f"{BASE_URL}/chat/message",
        json={"session_id": SESSION_ID, "message": msg}
    ).json()
    
    print(f"   State: {resp['state']}")
    print(f"   Complete: {resp['is_complete']}")
    print(f"   Data: {resp['data_collected']}")
    print(f"   Missing: {resp['missing_fields']}\n")
    time.sleep(1)

print("=" * 60)
print("AFTER MESSAGE 8, DATA SHOULD BE:")
print("- Name: Test Ahmed raza")
print("- Phone: 03124660742")  
print("- DOB: 01/15/2003")
print("- Service: cleaning")
print("- Insurance: cash_pay")