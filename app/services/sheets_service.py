import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json
from typing import Dict
from app.config.settings import settings


class SheetsService:
    def __init__(self):
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.sheet_id = settings.GOOGLE_SHEET_ID
        self.client = None
        self.sheet = None
        self._initialize()

    def _initialize(self):
        """Initialize Google Sheets connection"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]

            # Try to get credentials from environment variable first (production)
            creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')

            if creds_json:
                # Production: Use JSON from environment variable
                creds_dict = json.loads(creds_json)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict,
                    scope
                )
                print("✅ Using Google credentials from environment variable")
            else:
                # Development: Use file
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_file,
                    scope
                )
                print("✅ Using Google credentials from file")

            self.client = gspread.authorize(creds)
            self.sheet = self.client.open_by_key(self.sheet_id).sheet1
            print("✅ Google Sheets connected successfully!")

        except Exception as e:
            print(f"❌ Google Sheets connection failed: {e}")

    def log_booking(self, data: Dict) -> bool:
        """
        Log booking data to Google Sheet
        """
        print(f"📝 LOG_BOOKING called with data: {data}")

        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            row = [
                timestamp,
                data.get('caller_name', ''),
                data.get('phone_number', ''),
                data.get('symptoms', ''),
                data.get('preferred_date', ''),
                data.get('preferred_time', ''),
                data.get('doctor', ''),
                data.get('status', 'Pending'),
                data.get('session_id', ''),
                data.get('dob', '')
            ]

            self.sheet.append_row(row)
            print(f"✅ Logged booking for {data.get('caller_name')}")
            return True

        except Exception as e:
            print(f"❌ Failed to log to Google Sheets: {e}")
            raise Exception(f"Google Sheets logging failed: {e}")

    def log_call(self, caller_name: str, phone_number: str, session_id: str) -> bool:
        """Log incoming call (even if no booking made)"""
        try:
            data = {
                'caller_name': caller_name,
                'phone_number': phone_number,
                'symptoms': 'Call started',
                'preferred_date': '',
                'preferred_time': '',
                'doctor': '',
                'status': 'In Progress',
                'session_id': session_id,
                'dob': '',
            }
            return self.log_booking(data)
        except Exception as e:
            print(f"❌ Failed to log call: {e}")
            return False

    def update_booking_status(self, session_id: str, status: str) -> bool:
        """Update status of existing booking"""
        try:
            cell = self.sheet.find(session_id)
            if cell:
                row_num = cell.row
                status_col = 8  # Column H (Status)
                self.sheet.update_cell(row_num, status_col, status)
                print(f"✅ Updated booking status to: {status}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to update status: {e}")
            return False


# Singleton instance
sheets_service = SheetsService()
