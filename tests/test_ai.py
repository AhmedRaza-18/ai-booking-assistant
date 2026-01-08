"""
Test AI Service
Run this to verify AI is working correctly
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.ai_service import ai_service

print("="*50)
print("🧪 TESTING AI SERVICE")
print("="*50)

# Test 1: Simple greeting
print("\n📝 Test 1: Simple Greeting")
print("-" * 50)
user_input = "Hello, I need some help"
response = ai_service.chat(user_input)
print(f"User: {user_input}")
print(f"AI: {response}")

# Test 2: Service inquiry
print("\n📝 Test 2: Service Inquiry")
print("-" * 50)
conversation = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! I'm Alex. How can I help you today?"},
]
user_input = "I need a plumber for my house"
response = ai_service.chat(user_input, conversation)
print(f"User: {user_input}")
print(f"AI: {response}")

# Test 3: Budget question
print("\n📝 Test 3: Budget Question")
print("-" * 50)
conversation = [
    {"role": "user", "content": "I need a plumber"},
    {"role": "assistant", "content": "Great! What kind of plumbing work do you need?"},
]
user_input = "Fix a leaking pipe"
response = ai_service.chat(user_input, conversation)
print(f"User: {user_input}")
print(f"AI: {response}")

print("\n" + "="*50)
print("✅ AI SERVICE TESTS COMPLETE")
print("="*50)