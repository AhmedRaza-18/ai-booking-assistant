"""
Test Medical Clinic Lead Qualification
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.qualification import lead_qualifier, LeadStatus

print("="*70)
print("🏥 TESTING MEDICAL CLINIC QUALIFICATION")
print("="*70)

# Test 1: Fully qualified new patient
print("\n📝 Test 1: Qualified New Patient")
print("-" * 70)
patient1 = {
    "name": "Sarah Johnson",
    "phone": "+1-555-123-4567",
    "dob": "05/15/1985",
    "service": "cleaning",
    "insurance": "blue cross",
    "patient_type": "new",
    "urgency": "routine"
}
result1 = lead_qualifier.qualify_patient(patient1)
print(f"Patient: {patient1['name']}")
print(f"Status: {result1['status'].value}")
print(f"Priority: {result1['priority']}")
print(f"Score: {result1['score']}/100")
print(f"Next Steps: {result1['next_steps']}")

# Test 2: Emergency case
print("\n📝 Test 2: Emergency Case")
print("-" * 70)
patient2 = {
    "name": "Mike Chen",
    "phone": "+1-555-987-6543",
    "dob": "11/22/1992",
    "service": "emergency",
    "insurance": "aetna",
    "patient_type": "emergency",
    "urgency": "emergency",
    "notes": "Severe toothache, can't sleep"
}
result2 = lead_qualifier.qualify_patient(patient2)
print(f"Patient: {patient2['name']}")
print(f"Status: {result2['status'].value}")
print(f"Priority: {result2['priority']}")
print(f"Score: {result2['score']}/100")
print(f"Next Steps: {result2['next_steps']}")

# Test 3: Cash-pay patient
print("\n📝 Test 3: Cash-Pay Patient")
print("-" * 70)
patient3 = {
    "name": "Lisa Martinez",
    "phone": "+1-555-456-7890",
    "dob": "03/10/1978",
    "service": "whitening",
    "insurance": "cash_pay",
    "patient_type": "new",
    "urgency": "routine"
}
result3 = lead_qualifier.qualify_patient(patient3)
print(f"Patient: {patient3['name']}")
print(f"Status: {result3['status'].value}")
print(f"Score: {result3['score']}/100")
print(f"Reasons: {result3['reasons']}")

# Test 4: Missing information
print("\n📝 Test 4: Missing Information")
print("-" * 70)
patient4 = {
    "name": "Tom Wilson",
    "service": "checkup"
    # Missing: phone, dob, insurance
}
result4 = lead_qualifier.qualify_patient(patient4)
print(f"Patient: {patient4.get('name', 'Unknown')}")
print(f"Status: {result4['status'].value}")
print(f"Score: {result4['score']}/100")
print(f"Missing: {result4['missing_info']}")
print(f"Next Steps: {result4['next_steps']}")

# Test 5: Wrong insurance
print("\n📝 Test 5: Insurance Not Accepted")
print("-" * 70)
patient5 = {
    "name": "Amy Lee",
    "phone": "+1-555-222-3333",
    "dob": "07/18/1995",
    "service": "filling",
    "insurance": "some random insurance",
    "patient_type": "new",
    "urgency": "routine"
}
result5 = lead_qualifier.qualify_patient(patient5)
print(f"Patient: {patient5['name']}")
print(f"Status: {result5['status'].value}")
print(f"Reasons: {result5['reasons']}")
print(f"Next Steps: {result5['next_steps']}")

# Test 6: Urgency extraction
print("\n📝 Test 6: Urgency Level Detection")
print("-" * 70)
test_messages = [
    "I have severe pain and can't sleep",
    "I need an appointment today",
    "Can I come in this week?",
    "I'd like to schedule a routine cleaning"
]
for msg in test_messages:
    urgency = lead_qualifier.extract_urgency_level(msg)
    print(f"Message: '{msg}'")
    print(f"  → Urgency: {urgency}\n")

# Test 7: Insurance extraction
print("\n📝 Test 7: Insurance Provider Detection")
print("-" * 70)
test_messages = [
    "I have Blue Cross insurance",
    "I'll be paying cash",
    "Do you take Aetna?",
    "I don't have insurance"
]
for msg in test_messages:
    insurance = lead_qualifier.extract_insurance(msg)
    print(f"Message: '{msg}'")
    print(f"  → Insurance: {insurance}\n")

print("\n" + "="*70)
print("✅ MEDICAL CLINIC QUALIFICATION TESTS COMPLETE")
print("="*70)