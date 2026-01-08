import requests
import time

BASE_URL = 'http://localhost:8000'

print('🧪 TESTING FULL BOOKING FLOW WITH LOGGING...')

# Start fresh session
session_id = 'test-full-booking-001'

messages = [
    'Hi, I need an appointment',
    'I am a new patient',
    'I need a cleaning',
    'next week',
    'My name is Test Ahmed',
    'My phone is 03124660742',
    'My DOB is 01/15/2003',
    'I will pay cash',
    'Yes that is correct',
    'Monday morning',
    'Yes book it'
]

for i, msg in enumerate(messages, 1):
    print(f'\n{i}. Sending: {msg}')
    response = requests.post(f'{BASE_URL}/chat/message', json={
        'session_id': session_id,
        'message': msg
    })
    data = response.json()
    print(f'   State: {data["state"]}')
    print(f'   Complete: {data["is_complete"]}')
    if data['missing_fields']:
        print(f'   Missing: {data["missing_fields"]}')

    time.sleep(1)

print('\n✅ Full booking test completed')