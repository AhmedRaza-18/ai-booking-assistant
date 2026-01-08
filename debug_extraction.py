import requests
import time

BASE_URL = 'http://localhost:8000'

print('🔍 DEBUGGING DATA EXTRACTION...')

# Start fresh session
session_id = 'debug-extraction-001'

# Test each field extraction individually
test_cases = [
    ('Hi, I need an appointment', 'greeting'),
    ('I am a new patient', 'identify_patient'),
    ('I need a cleaning', 'get_service'),
    ('next week', 'check_urgency'),
    ('My name is Debug Test', 'collect_name'),
    ('My phone is 03124660742', 'collect_phone'),
    ('My DOB is 01/15/2003', 'collect_dob'),
    ('I will pay cash', 'collect_insurance'),
]

for msg, expected_state in test_cases:
    print(f'\n📤 Sending: "{msg}"')
    response = requests.post(f'{BASE_URL}/chat/message', json={
        'session_id': session_id,
        'message': msg
    })
    data = response.json()
    print(f'   State: {data["state"]} (expected: {expected_state})')
    print(f'   AI Response: {data["response"][:100]}...')
    print(f'   Data: {data["data_collected"]}')

    time.sleep(1)

print('\n✅ Debug test completed')