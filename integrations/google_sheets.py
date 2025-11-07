"""
Google Sheets API integration.

Provides functionality to interact with Google Sheets API for:
- Reading client data
- Adding client data
- Posting call/interaction data
"""
from __future__ import annotations

import os
from typing import Dict, Any, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Scopes required for Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsClient:
    """Client for interacting with Google Sheets API.
    
    Handles authentication and provides methods for sheet operations.
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        spreadsheet_id: Optional[str] = None,
    ):
        """Initialize Google Sheets client.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
            spreadsheet_id: Google Sheets spreadsheet ID
        """
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_PATH",
            "credentials.json"
        )
        self.token_path = token_path or os.getenv(
            "GOOGLE_SHEETS_TOKEN_PATH",
            "token.json"
        )
        self.spreadsheet_id = spreadsheet_id or os.getenv(
            "GOOGLE_SHEETS_SPREADSHEET_ID"
        )
        self.service = None
        if self.spreadsheet_id:
            self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Sheets API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
            except Exception:
                pass
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=creds)
    
    def get_clients(
        self,
        sheet_name: Optional[str] = None,
        range_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get client data from Google Sheets.
        
        Args:
            sheet_name: Name of the sheet tab (default: first sheet)
            range_name: A1 notation range (e.g., "A1:D10") or None for all data
            
        Returns:
            Dictionary with clients data
        """
        try:
            if not self.service:
                return {
                    "error": "Google Sheets not configured",
                    "clients": [],
                    "count": 0
                }
            
            # Determine range
            if range_name:
                if sheet_name:
                    range_str = f"{sheet_name}!{range_name}"
                else:
                    range_str = range_name
            elif sheet_name:
                range_str = sheet_name
            else:
                # Get first sheet name
                sheet_metadata = self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                sheets = sheet_metadata.get('sheets', [])
                if not sheets:
                    return {
                        "error": "No sheets found in spreadsheet",
                        "clients": [],
                        "count": 0
                    }
                range_str = sheets[0].get('properties', {}).get('title', 'Sheet1')
            
            # Read data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_str
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return {
                    "clients": [],
                    "count": 0,
                    "message": "No data found in sheet"
                }
            
            # First row is headers
            headers = values[0] if values else []
            clients = []
            
            # Convert rows to dictionaries
            for row in values[1:]:
                client = {}
                for i, header in enumerate(headers):
                    client[header] = row[i] if i < len(row) else ""
                clients.append(client)
            
            return {
                "clients": clients,
                "count": len(clients),
                "headers": headers,
                "message": f"Retrieved {len(clients)} clients"
            }
        except HttpError as error:
            return {
                "error": f"Error reading clients: {str(error)}",
                "clients": [],
                "count": 0
            }
    
    def add_clients(
        self,
        clients: List[Dict[str, Any]],
        sheet_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add client data to Google Sheets.
        
        Args:
            clients: List of client dictionaries to add
            sheet_name: Name of the sheet tab (default: first sheet)
            
        Returns:
            Dictionary with operation result
        """
        try:
            if not self.service:
                return {
                    "success": False,
                    "error": "Google Sheets not configured",
                    "message": "Google Sheets not configured"
                }
            
            if not clients:
                return {
                    "success": False,
                    "error": "No clients provided",
                    "message": "No clients provided"
                }
            
            # Get sheet name
            if not sheet_name:
                sheet_metadata = self.service.spreadsheets().get(
                    spreadsheetId=self.spreadsheet_id
                ).execute()
                sheets = sheet_metadata.get('sheets', [])
                if not sheets:
                    return {
                        "success": False,
                        "error": "No sheets found in spreadsheet",
                        "message": "No sheets found in spreadsheet"
                    }
                sheet_name = sheets[0].get('properties', {}).get('title', 'Sheet1')
            
            # Get headers to determine column order
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=f"{sheet_name}!A1:Z1"
            ).execute()
            
            headers = result.get('values', [[]])[0] if result.get('values') else []
            
            # If no headers, use keys from first client
            if not headers and clients:
                headers = list(clients[0].keys())
                # Write headers first
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
            
            # Prepare rows
            rows = []
            for client in clients:
                row = [client.get(header, "") for header in headers]
                rows.append(row)
            
            # Append rows
            range_str = f"{sheet_name}!A:Z"
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': rows}
            ).execute()
            
            return {
                "success": True,
                "added_count": len(clients),
                "message": f"Successfully added {len(clients)} client(s)"
            }
        except HttpError as error:
            return {
                "success": False,
                "error": f"Error adding clients: {str(error)}",
                "message": f"Failed to add clients: {str(error)}"
            }
    
    def post_call_data(
        self,
        call_data: Dict[str, Any],
        sheet_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Post call/interaction data to Google Sheets.
        
        Args:
            call_data: Dictionary with call data to append
            sheet_name: Name of the sheet tab (default: first sheet or "Calls")
            
        Returns:
            Dictionary with operation result
        """
        try:
            if not self.service:
                return {
                    "success": False,
                    "error": "Google Sheets not configured",
                    "message": "Google Sheets not configured"
                }
            
            # Default to "Calls" sheet if not specified
            if not sheet_name:
                sheet_name = os.getenv("GOOGLE_SHEETS_CALLS_SHEET_NAME", "Calls")
            
            # Get headers to determine column order
            try:
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1:Z1"
                ).execute()
                headers = result.get('values', [[]])[0] if result.get('values') else []
            except HttpError:
                # Sheet might not exist or be empty, create headers from call_data keys
                headers = list(call_data.keys())
                # Write headers first
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=f"{sheet_name}!A1",
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
            
            # Prepare row
            row = [call_data.get(header, "") for header in headers]
            
            # Append row
            range_str = f"{sheet_name}!A:Z"
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_str,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row]}
            ).execute()
            
            return {
                "success": True,
                "message": "Call data posted successfully"
            }
        except HttpError as error:
            return {
                "success": False,
                "error": f"Error posting call data: {str(error)}",
                "message": f"Failed to post call data: {str(error)}"
            }


def get_google_sheets_client() -> Optional[GoogleSheetsClient]:
    """Factory function to get configured Google Sheets client.
    
    Returns:
        GoogleSheetsClient instance if configured, None otherwise.
    """
    try:
        credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        token_path = os.getenv("GOOGLE_SHEETS_TOKEN_PATH")
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        
        if not credentials_path or not spreadsheet_id:
            return None
        
        return GoogleSheetsClient(
            credentials_path=credentials_path,
            token_path=token_path,
            spreadsheet_id=spreadsheet_id,
        )
    except Exception:
        return None

