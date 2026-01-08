import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
from typing import Dict, Optional
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
            
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_file, 
                scope
            )
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(self.sheet_id)
            worksheets = spreadsheet.worksheets()
            print(f"📊 Spreadsheet has {len(worksheets)} worksheets:")
            for ws in worksheets:
                print(f"  - {ws.title} (rows: {ws.row_count}, cols: {ws.col_count})")
            
            self.sheet = spreadsheet.sheet1  # Use the first worksheet
            print(f"📊 Using worksheet: {self.sheet.title}")
            print(f"📊 Sheet URL: https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit")
            
            # Check current sheet contents
            try:
                all_values = self.sheet.get_all_values()
                print(f"📊 Sheet has {len(all_values)} rows")
                if all_values:
                    print(f"📊 First row: {all_values[0]}")
                    print(f"📊 Last row: {all_values[-1]}")
            except Exception as e:
                print(f"❌ Could not read sheet contents: {e}")
        except Exception as e:
            print(f"❌ Google Sheets connection failed: {e}")
    
    def log_booking(self, data: Dict) -> bool:
        """
        Log booking data to Google Sheet
        
        Expected data format:
        {
            'caller_name': str,
            'phone_number': str,
            'symptoms': str,
            'preferred_date': str,
            'preferred_time': str,
            'doctor': str,
            'status': str (e.g., 'Pending', 'Confirmed', 'Cancelled'),
            'session_id': str
                'dob': dob,
           
        }
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
            print(f"✅ Logged booking for {data.get('caller_name')} to Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Failed to log to Google Sheets: {e}")
            raise Exception(f"Google Sheets logging failed: {e}")  # Raise to show error in API
    
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
            # Find the row with matching session_id
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

# Create singleton instance
sheets_service = SheetsService()