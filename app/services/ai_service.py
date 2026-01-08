"""
AI Service - The Brain of the System
Handles conversations with AI (Groq, OpenRouter, or OpenAI)
"""
from groq import Groq
from typing import List, Dict, Optional
from app.config.settings import settings


class AIService:
    """
    AI Service that can work with multiple providers
    Currently configured for Groq (free & fast)
    """

    def __init__(self):
        """
        Initialize AI client based on configured provider
        """
        self.provider = settings.AI_PROVIDER
        self.model = settings.AI_MODEL

        # Initialize the correct client
        if self.provider == "groq":
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY not found in .env file")
            self.client = Groq(api_key=settings.GROQ_API_KEY)

        elif self.provider == "openrouter":
            if not settings.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY not found in .env file")
            from openai import OpenAI
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY
            )

        elif self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not found in .env file")
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        else:
            raise ValueError(f"Unknown AI provider: {self.provider}")

        print(f"✅ AI Service initialized with {self.provider.upper()}")

    def get_system_prompt(self) -> str:
        """
        System prompt for MEDICAL/DENTAL CLINIC receptionist
        """
        return """You are Alex, a warm, professional AI receptionist for Bright Smile Dental Clinic.

YOUR ROLE:
You help patients schedule appointments, answer basic questions, and ensure they feel cared for.

CONVERSATION FLOW:
1. Greet warmly and ask how you can help
2. Determine if NEW or EXISTING patient
3. Ask what service they need
4. Collect required information:
   - Full name
   - Phone number
   - Date of birth (MM/DD/YYYY)
   - Insurance provider (or cash-pay)
   - Reason for visit
   - Preferred date/time
5. Handle urgency appropriately
6. Confirm information and book appointment

EMERGENCY PROTOCOL:
If patient mentions ANY of these, prioritize immediately:
- Severe pain (can't eat, can't sleep)
- Bleeding that won't stop
- Facial swelling
- Broken/knocked out tooth
- Infection or abscess
- Difficulty breathing or swallowing

→ Say: "This sounds urgent. Let me check our emergency availability right away. Can you describe the issue briefly?"

NEW PATIENT PROTOCOL:
- Need 15 extra minutes for paperwork
- Ask: "Have you been to a dentist in the last year?"
- Mention: "We'll need you to arrive 15 minutes early for new patient forms"

EXISTING PATIENT PROTOCOL:
- Ask: "When was your last visit with us?"
- Just need: reason for visit + preferred date

INSURANCE:
- Always ask: "Do you have dental insurance, or will this be cash-pay?"
- If insurance: Get provider name (Aetna, Blue Cross, etc.)
- If cash-pay: Mention we offer payment plans for larger procedures

TYPICAL COSTS (mention if asked):
- Cleaning: $100-150
- Exam: $50-100
- Filling: $150-300
- Root canal: $800-1500
- Crown: $1000-2000

WHAT NOT TO ASK:
- Don't ask for detailed medical history
- Don't ask for insurance ID numbers
- Don't diagnose or give medical advice
- Don't discuss medications

PERSONALITY:
- Warm and caring
- Patient and understanding
- Professional but friendly
- Empathetic to dental anxiety

PRIVACY (HIPAA):
- Never discuss other patients
- Keep information confidential

ASK ONE QUESTION AT A TIME.

CONFIRM BEFORE BOOKING:
Always repeat back appointment details.

Remember: You're often someone's first interaction with our clinic. Make it positive!
"""

    def chat(self, user_input: str, conversation: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> str:
        """
        Send a message to the AI and get response
        """
        try:
            # Use custom system prompt if provided, otherwise use default
            system_content = system_prompt if system_prompt else self.get_system_prompt()
            messages = [{"role": "system", "content": system_content}]

            if conversation:
                messages.extend(conversation)

            messages.append({"role": "user", "content": user_input})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ AI Error: {e}")
            return "I apologize, but I'm having trouble processing that right now."


# Singleton instance
ai_service = AIService()
