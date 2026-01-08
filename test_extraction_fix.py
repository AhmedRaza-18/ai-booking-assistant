import requests
import time

BASE_URL = 'http://localhost:8000'

print('🧪 TESTING DATA EXTRACTION FIX...')

# Start fresh session
session_id = 'test-fix-001'

# Test 1: Name extraction
print('\n1. Testing name extraction...')
response = requests.post(f'{BASE_URL}/chat/message', json={
    'session_id': session_id,
    'message': 'Hi, I need an appointment'
})
print(f'State: {response.json()["state"]}')

response = requests.post(f'{BASE_URL}/chat/message', json={
    'session_id': session_id,
    'message': 'I am a new patient'
})
print(f'State: {response.json()["state"]}')

response = requests.post(f'{BASE_URL}/chat/message', json={
    'session_id': session_id,
    'message': 'cleaning'
})
print(f'State: {response.json()["state"]}')

response = requests.post(f'{BASE_URL}/chat/message', json={
    'session_id': session_id,
    'message': 'next week'
})
print(f'State: {response.json()["state"]}')

# Test name extraction
response = requests.post(f'{BASE_URL}/chat/message', json={
    'session_id': session_id,
    'message': 'My name is Test Ahmed'
})
data = response.json()
print(f'State: {data["state"]}')
print(f'Name extracted: {data["data_collected"]["name"]}')

print('✅ Test completed')