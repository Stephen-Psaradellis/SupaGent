"""
Google Calendar API integration.

Provides functionality to interact with Google Calendar API for:
- Checking availability
- Getting user bookings
- Creating appointments
- Modifying appointments
- Canceling appointments
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Scopes required for Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarClient:
    """Client for interacting with Google Calendar API.
    
    Handles authentication and provides methods for calendar operations.
    """
    
    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        calendar_id: Optional[str] = "primary",
    ):
        """Initialize Google Calendar client.
        
        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
            calendar_id: Calendar ID to use (default: "primary")
        """
        self.credentials_path = credentials_path or os.getenv(
            "GOOGLE_CALENDAR_CREDENTIALS_PATH",
            "credentials.json"
        )
        self.token_path = token_path or os.getenv(
            "GOOGLE_CALENDAR_TOKEN_PATH",
            "token.json"
        )
        self.calendar_id = calendar_id or os.getenv(
            "GOOGLE_CALENDAR_ID",
            "primary"
        )
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Authenticate with Google Calendar API."""
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
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def check_availability(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        duration_minutes: int = 30,
    ) -> Dict[str, Any]:
        """Check calendar availability for a time range.
        
        Args:
            time_min: Start time for availability check (default: now)
            time_max: End time for availability check (default: now + 7 days)
            duration_minutes: Minimum duration needed for availability
            
        Returns:
            Dictionary with availability information including:
            - available_slots: List of available time slots
            - busy_periods: List of busy periods
            - summary: Summary of availability
        """
        try:
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=7)
            
            # Format times for API
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            # Get busy periods
            freebusy_query = {
                "timeMin": time_min_str,
                "timeMax": time_max_str,
                "items": [{"id": self.calendar_id}]
            }
            
            freebusy_result = self.service.freebusy().query(
                body=freebusy_query
            ).execute()
            
            busy_periods = freebusy_result.get('calendars', {}).get(
                self.calendar_id, {}
            ).get('busy', [])
            
            # Get all events for more details
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Calculate available slots
            available_slots = self._calculate_available_slots(
                time_min, time_max, busy_periods, duration_minutes
            )
            
            return {
                "available_slots": available_slots,
                "busy_periods": busy_periods,
                "events": [
                    {
                        "id": event.get('id'),
                        "summary": event.get('summary', 'No title'),
                        "start": event.get('start', {}).get('dateTime') or event.get('start', {}).get('date'),
                        "end": event.get('end', {}).get('dateTime') or event.get('end', {}).get('date'),
                    }
                    for event in events
                ],
                "summary": f"Found {len(available_slots)} available slots"
            }
        except HttpError as error:
            return {
                "error": f"Error checking availability: {str(error)}",
                "available_slots": [],
                "busy_periods": [],
                "events": [],
                "summary": "Error checking availability"
            }
    
    def _calculate_available_slots(
        self,
        time_min: datetime,
        time_max: datetime,
        busy_periods: List[Dict[str, str]],
        duration_minutes: int,
    ) -> List[Dict[str, str]]:
        """Calculate available time slots between busy periods.
        
        Args:
            time_min: Start of time range
            time_max: End of time range
            busy_periods: List of busy periods with 'start' and 'end' keys
            duration_minutes: Minimum duration for a slot
            
        Returns:
            List of available time slots
        """
        available_slots = []
        current_time = time_min
        
        # Sort busy periods by start time
        sorted_busy = sorted(
            busy_periods,
            key=lambda x: datetime.fromisoformat(x['start'].replace('Z', '+00:00'))
        )
        
        for busy in sorted_busy:
            busy_start = datetime.fromisoformat(
                busy['start'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            busy_end = datetime.fromisoformat(
                busy['end'].replace('Z', '+00:00')
            ).replace(tzinfo=None)
            
            # If there's a gap before this busy period
            if current_time < busy_start:
                slot_duration = (busy_start - current_time).total_seconds() / 60
                if slot_duration >= duration_minutes:
                    available_slots.append({
                        "start": current_time.isoformat(),
                        "end": busy_start.isoformat(),
                        "duration_minutes": int(slot_duration)
                    })
            
            # Move current time past this busy period
            if busy_end > current_time:
                current_time = busy_end
        
        # Check for available time after last busy period
        if current_time < time_max:
            slot_duration = (time_max - current_time).total_seconds() / 60
            if slot_duration >= duration_minutes:
                available_slots.append({
                    "start": current_time.isoformat(),
                    "end": time_max.isoformat(),
                    "duration_minutes": int(slot_duration)
                })
        
        return available_slots
    
    def get_user_bookings(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50,
    ) -> Dict[str, Any]:
        """Get user's calendar bookings/appointments.
        
        Args:
            time_min: Start time for query (default: now)
            time_max: End time for query (default: now + 30 days)
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with bookings information
        """
        try:
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=30)
            
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            bookings = []
            for event in events:
                start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
                end = event.get('end', {}).get('dateTime') or event.get('end', {}).get('date')
                
                bookings.append({
                    "id": event.get('id'),
                    "summary": event.get('summary', 'No title'),
                    "description": event.get('description', ''),
                    "start": start,
                    "end": end,
                    "location": event.get('location', ''),
                    "attendees": [
                        attendee.get('email')
                        for attendee in event.get('attendees', [])
                    ],
                    "status": event.get('status', 'confirmed'),
                })
            
            return {
                "bookings": bookings,
                "count": len(bookings),
                "summary": f"Found {len(bookings)} bookings"
            }
        except HttpError as error:
            return {
                "error": f"Error getting bookings: {str(error)}",
                "bookings": [],
                "count": 0,
                "summary": "Error retrieving bookings"
            }
    
    def book_appointment(
        self,
        summary: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new appointment/event in the calendar.
        
        Args:
            summary: Event title/summary
            start_time: Start time of the appointment
            end_time: End time of the appointment
            description: Optional description
            location: Optional location
            attendees: Optional list of attendee email addresses
            
        Returns:
            Dictionary with created event information
        """
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if description:
                event['description'] = description
            if location:
                event['location'] = location
            if attendees:
                event['attendees'] = [
                    {'email': email} for email in attendees
                ]
                event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                }
            
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "summary": created_event.get('summary'),
                "start": created_event.get('start', {}).get('dateTime'),
                "end": created_event.get('end', {}).get('dateTime'),
                "html_link": created_event.get('htmlLink'),
                "message": f"Appointment '{summary}' created successfully"
            }
        except HttpError as error:
            return {
                "success": False,
                "error": f"Error creating appointment: {str(error)}",
                "message": f"Failed to create appointment: {str(error)}"
            }
    
    def modify_appointment(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing appointment/event.
        
        Args:
            event_id: ID of the event to update
            summary: New summary/title (optional)
            start_time: New start time (optional)
            end_time: New end time (optional)
            description: New description (optional)
            location: New location (optional)
            attendees: New list of attendees (optional)
            
        Returns:
            Dictionary with updated event information
        """
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                }
            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                }
            if description is not None:
                event['description'] = description
            if location is not None:
                event['location'] = location
            if attendees is not None:
                event['attendees'] = [
                    {'email': email} for email in attendees
                ]
            
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": updated_event.get('id'),
                "summary": updated_event.get('summary'),
                "start": updated_event.get('start', {}).get('dateTime'),
                "end": updated_event.get('end', {}).get('dateTime'),
                "html_link": updated_event.get('htmlLink'),
                "message": f"Appointment '{updated_event.get('summary')}' updated successfully"
            }
        except HttpError as error:
            return {
                "success": False,
                "error": f"Error updating appointment: {str(error)}",
                "message": f"Failed to update appointment: {str(error)}"
            }
    
    def cancel_appointment(self, event_id: str) -> Dict[str, Any]:
        """Cancel/delete an appointment/event.
        
        Args:
            event_id: ID of the event to cancel
            
        Returns:
            Dictionary with cancellation result
        """
        try:
            # Get event details before deletion
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            summary = event.get('summary', 'Unknown')
            
            # Delete the event
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "event_id": event_id,
                "message": f"Appointment '{summary}' cancelled successfully"
            }
        except HttpError as error:
            return {
                "success": False,
                "error": f"Error cancelling appointment: {str(error)}",
                "message": f"Failed to cancel appointment: {str(error)}"
            }


def get_google_calendar_client() -> Optional[GoogleCalendarClient]:
    """Factory function to get configured Google Calendar client.
    
    Returns:
        GoogleCalendarClient instance if configured, None otherwise.
    """
    try:
        credentials_path = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
        token_path = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH")
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        
        if not credentials_path:
            return None
        
        return GoogleCalendarClient(
            credentials_path=credentials_path,
            token_path=token_path,
            calendar_id=calendar_id,
        )
    except Exception:
        return None

