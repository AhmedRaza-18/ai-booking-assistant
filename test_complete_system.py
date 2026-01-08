"""
Complete System Test
Tests entire booking flow with all integrations
"""
import requests
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = f"system-test-{int(time.time())}"

def test_booking_flow():
    """Test complete booking flow"""
    print("🔥 TESTING COMPLETE SYSTEM")
    print("=" * 60)
    print(f"Session ID: {SESSION_ID}\n")
    
    # Conversation steps
    messages = [
        "Hi, I need an appointment",
        "I am a new patient",
        "I need a teeth cleaning",
        "Next week would be good",
        "My name is Test Ahmed raza",
        "My phone is 03124660742",
        "01/15/2003",
        "I will pay cash",
        "Yes that is correct",
        "Monday morning works",
        "Yes please book it"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. User: {message}")
        
        response = requests.post(
            f"{BASE_URL}/chat/message",
            json={"session_id": SESSION_ID, "message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   AI: {data['response'][:100]}...")
            print(f"   State: {data['state']}")
            print(f"   Complete: {data['is_complete']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            break
        
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETE")
    print("\n🔍 CHECKING RESULTS...")
    
    # Check database
    print("\n1. Database - Recent Conversations:")
    stats = requests.get(f"{BASE_URL}/admin/stats").json()
    print(f"   Total: {stats['total_conversations']}")
    print(f"   Completed: {stats['completed_bookings']}")
    
    # Check conversation details
    print("\n2. Database - This Conversation:")
    conv = requests.get(f"{BASE_URL}/admin/conversation/{SESSION_ID}").json()
    print(f"   State: {conv.get('state')}")
    print(f"   Patient: {conv.get('data', {}).get('name')}")
    print(f"   Phone: {conv.get('data', {}).get('phone')}")
    
    print("\n3. Google Sheets:")
    print("   ✅ Check: https://docs.google.com/spreadsheets/d/1lu5CMAcsz2r9eWSHD_fRL0HGsM5CPJr71OBLmDsTlVE/")
    
    print("\n4. SMS (if number verified):")
    print("   Check phone for confirmation message")
    
    print("\n" + "=" * 60)
    print("🎉 ALL SYSTEMS TESTED!")

if __name__ == "__main__":
    test_booking_flow()