"""
Lead Qualification Service - MEDICAL/DENTAL CLINIC VERSION
Determines if a patient/lead meets clinic requirements
Combines AI conversation with healthcare business rules
"""
from typing import Dict, Optional, List
from enum import Enum


class LeadStatus(Enum):
    """
    Possible patient qualification statuses
    """
    QUALIFIED = "qualified"           # Ready to book appointment
    NOT_QUALIFIED = "not_qualified"   # Doesn't meet criteria (wrong insurance, outside service area)
    NEEDS_MORE_INFO = "needs_info"    # Still collecting information
    EMERGENCY = "emergency"            # Needs immediate attention
    TRANSFER_TO_HUMAN = "transfer"    # Too complex for AI


class QualificationRules:
    """
    Business rules for MEDICAL/DENTAL CLINIC patient qualification
    CUSTOMIZE THESE for each clinic client
    """
    
    # ============================================
    # CLINIC INFORMATION
    # ============================================
    CLINIC_NAME = "Bright Smile Dental Clinic"
    CLINIC_TYPE = "dental"  # dental, medical, pediatric, etc.
    
    # ============================================
    # BUDGET RULES (For cash-pay patients)
    # ============================================
    # Most medical clinics work with insurance, but include for cash patients
    MIN_BUDGET = 0        # No minimum for medical
    MAX_BUDGET = 100000   # High ceiling for procedures
    
    # Typical costs (for patient information)
    TYPICAL_COSTS = {
        "cleaning": "$100-150",
        "exam": "$50-100",
        "filling": "$150-300",
        "root canal": "$800-1500",
        "crown": "$1000-2000",
        "extraction": "$200-500",
        "whitening": "$300-800"
    }
    
    # ============================================
    # TIMELINE/URGENCY RULES
    # ============================================
    URGENT_KEYWORDS = [
        "emergency", "urgent", "severe pain", "bleeding", 
        "swelling", "broken tooth", "knocked out tooth",
        "accident", "trauma", "can't eat", "can't sleep",
        "unbearable", "excruciating"
    ]
    
    SAME_DAY_KEYWORDS = [
        "today", "right now", "asap", "immediately",
        "as soon as possible"
    ]
    
    # ============================================
    # SERVICE CATEGORIES
    # ============================================
    VALID_SERVICES = [
        # Routine Services
        "cleaning", "checkup", "exam", "consultation",
        "x-ray", "screening",
        
        # Restorative
        "filling", "cavity", "crown", "bridge", 
        "root canal", "extraction", "implant",
        
        # Cosmetic
        "whitening", "veneers", "bonding",
        
        # Orthodontics
        "braces", "invisalign", "retainer",
        
        # Emergency
        "emergency", "pain", "toothache", "broken tooth",
        "abscess", "infection"
    ]
    
    # ============================================
    # INSURANCE PROVIDERS
    # ============================================
    ACCEPTED_INSURANCE = [
        "aetna",
        "blue cross",
        "blue shield",
        "cigna",
        "delta dental",
        "guardian",
        "humana",
        "metlife",
        "united healthcare",
        "medicare",
        "medicaid"
    ]
    
    # ============================================
    # PATIENT TYPES
    # ============================================
    PATIENT_TYPES = [
        "new patient",
        "existing patient",
        "emergency",
        "referral"
    ]
    
    # ============================================
    # AGE RESTRICTIONS
    # ============================================
    MIN_AGE = 0           # 0 = all ages
    MAX_AGE = 120         # No maximum
    PEDIATRIC_ONLY = False  # Set True for pediatric-only clinics
    ADULT_ONLY = False      # Set True for adult-only clinics
    
    # ============================================
    # REQUIRED INFORMATION
    # ============================================
    REQUIRED_FIELDS = [
        "name",           # Patient full name
        "phone",          # Contact phone
        "dob",            # Date of birth (for medical records)
        "service",        # What they need
        "insurance_or_cash"  # Insurance provider or cash-pay
    ]
    
    OPTIONAL_FIELDS = [
        "email",          # Email address
        "address",        # Physical address
        "preferred_date", # Preferred appointment date
        "preferred_time", # Preferred appointment time
        "notes"           # Additional notes
    ]


class LeadQualifier:
    """
    Qualifies patients/leads for medical clinic
    """
    
    def __init__(self, rules: Optional[QualificationRules] = None):
        """
        Initialize with qualification rules
        """
        self.rules = rules or QualificationRules()
    
    
    def extract_urgency_level(self, text: str) -> str:
        """
        Determine urgency level from patient message
        
        Returns:
            "emergency", "urgent", "same_day", "routine"
        """
        text = text.lower()
        
        # Check for emergency keywords
        for keyword in self.rules.URGENT_KEYWORDS:
            if keyword in text:
                return "emergency"
        
        # Check for same-day requests
        for keyword in self.rules.SAME_DAY_KEYWORDS:
            if keyword in text:
                return "same_day"
        
        # Check for "this week"
        if any(phrase in text for phrase in ["this week", "within a week", "few days"]):
            return "urgent"
        
        # Everything else is routine
        return "routine"
    
    
    def extract_patient_type(self, text: str) -> Optional[str]:
        """
        Determine if new or existing patient
        
        Returns:
            "new", "existing", "emergency", or None
        """
        text = text.lower()
        
        # Emergency overrides everything
        if self.extract_urgency_level(text) == "emergency":
            return "emergency"
        
        # Check for new patient indicators
        if any(phrase in text for phrase in [
            "new patient", "first time", "never been", 
            "new here", "first visit"
        ]):
            return "new"
        
        # Check for existing patient indicators
        if any(phrase in text for phrase in [
            "existing", "current patient", "been here before", 
            "regular patient", "returning", "come here before"
        ]):
            return "existing"
        
        return None
    
    
    def extract_service_type(self, text: str) -> Optional[str]:
        """
        Extract service type from text
        
        Args:
            text: Patient's message
        
        Returns:
            Service type or None
        """
        text = text.lower()
        
        for service in self.rules.VALID_SERVICES:
            if service in text:
                return service
        
        # Common synonyms
        if "teeth cleaning" in text or "dental cleaning" in text:
            return "cleaning"
        if "check up" in text or "check-up" in text:
            return "checkup"
        if "hurt" in text or "ache" in text:
            return "pain"
        
        return None
    
    
    def extract_insurance(self, text: str) -> Optional[str]:
        """
        Extract insurance provider from text
        
        Returns:
            Insurance provider name or "cash_pay"
        """
        text = text.lower()
        
        # Check for cash-pay indicators
        if any(phrase in text for phrase in [
            "no insurance", "cash", "self pay", "self-pay",
            "out of pocket", "paying myself", "don't have insurance"
        ]):
            return "cash_pay"
        
        # Check against accepted insurance list
        for insurance in self.rules.ACCEPTED_INSURANCE:
            if insurance in text:
                return insurance
        
        return None
    
    
    def check_insurance_qualification(self, insurance: Optional[str]) -> Dict:
        """
        Check if insurance is accepted
        
        Returns:
            {"qualified": bool, "reason": str}
        """
        if insurance is None:
            return {
                "qualified": None,
                "reason": "Insurance information not provided"
            }
        
        if insurance == "cash_pay":
            return {
                "qualified": True,
                "reason": "Cash-pay patient accepted"
            }
        
        if insurance in self.rules.ACCEPTED_INSURANCE:
            return {
                "qualified": True,
                "reason": f"{insurance.title()} insurance is accepted"
            }
        
        return {
            "qualified": False,
            "reason": f"{insurance.title()} is not in our network"
        }
    
    
    def check_urgency_qualification(self, urgency: str) -> Dict:
        """
        Determine how to handle based on urgency
        
        Returns:
            {"priority": str, "action": str, "reason": str}
        """
        if urgency == "emergency":
            return {
                "priority": "CRITICAL",
                "action": "offer_immediate_appointment_or_transfer",
                "reason": "Emergency requires immediate attention"
            }
        
        if urgency == "same_day":
            return {
                "priority": "HIGH",
                "action": "check_same_day_availability",
                "reason": "Patient needs same-day appointment"
            }
        
        if urgency == "urgent":
            return {
                "priority": "MEDIUM",
                "action": "prioritize_this_week",
                "reason": "Patient needs appointment within a week"
            }
        
        return {
            "priority": "NORMAL",
            "action": "book_routine_appointment",
            "reason": "Routine appointment"
        }
    
    
    def qualify_patient(self, patient_data: Dict) -> Dict:
        """
        Main qualification function for medical clinic
        Analyzes all collected data and makes final decision
        
        Args:
            patient_data: Dictionary with patient information
            {
                "name": str,
                "phone": str,
                "email": str (optional),
                "dob": str,
                "service": str,
                "insurance": str,
                "patient_type": str,
                "urgency": str,
                "notes": str (optional)
            }
        
        Returns:
            {
                "status": LeadStatus,
                "priority": str,
                "score": int (0-100),
                "reasons": List[str],
                "missing_info": List[str],
                "next_steps": str
            }
        """
        reasons = []
        missing_info = []
        score = 0
        
        # ============================================
        # CHECK REQUIRED FIELDS
        # ============================================
        
        # Name (15 points)
        if not patient_data.get("name"):
            missing_info.append("patient name")
        else:
            score += 15
            reasons.append("Patient name collected")
        
        # Phone (20 points - critical for contact)
        if not patient_data.get("phone"):
            missing_info.append("phone number")
        else:
            score += 20
            reasons.append("Contact phone collected")
        
        # Date of Birth (15 points - needed for medical records)
        if not patient_data.get("dob"):
            missing_info.append("date of birth")
        else:
            score += 15
            reasons.append("Date of birth collected")
        
        # Service Type (20 points)
        if not patient_data.get("service"):
            missing_info.append("service/procedure needed")
        else:
            score += 20
            reasons.append(f"Service requested: {patient_data.get('service')}")
        
        # ============================================
        # CHECK INSURANCE
        # ============================================
        insurance_check = self.check_insurance_qualification(
            patient_data.get("insurance")
        )
        
        if insurance_check["qualified"] is True:
            score += 15
            reasons.append(insurance_check["reason"])
        elif insurance_check["qualified"] is False:
            reasons.append(insurance_check["reason"])
            return {
                "status": LeadStatus.NOT_QUALIFIED,
                "priority": "LOW",
                "score": score,
                "reasons": reasons,
                "missing_info": missing_info,
                "next_steps": "Politely explain we don't accept their insurance. Offer to check if they'd like to pay cash."
            }
        else:
            missing_info.append("insurance information")
        
        # ============================================
        # CHECK URGENCY
        # ============================================
        urgency = patient_data.get("urgency", "routine")
        urgency_check = self.check_urgency_qualification(urgency)
        
        if urgency == "emergency":
            score += 15
            reasons.append(urgency_check["reason"])
            return {
                "status": LeadStatus.EMERGENCY,
                "priority": urgency_check["priority"],
                "score": score,
                "reasons": reasons,
                "missing_info": missing_info,
                "next_steps": "Transfer to staff immediately or offer emergency appointment"
            }
        else:
            score += 15
            reasons.append(urgency_check["reason"])
        
        # ============================================
        # DETERMINE FINAL STATUS
        # ============================================
        
        # If missing critical info
        if missing_info:
            return {
                "status": LeadStatus.NEEDS_MORE_INFO,
                "priority": urgency_check["priority"],
                "score": score,
                "reasons": reasons,
                "missing_info": missing_info,
                "next_steps": f"Ask for: {', '.join(missing_info)}"
            }
        
        # Fully qualified
        if score >= 85:
            return {
                "status": LeadStatus.QUALIFIED,
                "priority": urgency_check["priority"],
                "score": score,
                "reasons": reasons,
                "missing_info": [],
                "next_steps": urgency_check["action"]
            }
        
        # Partially qualified (needs review)
        return {
            "status": LeadStatus.NEEDS_MORE_INFO,
            "priority": urgency_check["priority"],
            "score": score,
            "reasons": reasons,
            "missing_info": missing_info,
            "next_steps": "Collect remaining information"
        }


# Create singleton instance
lead_qualifier = LeadQualifier()