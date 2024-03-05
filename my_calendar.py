#

from datetime import datetime, timedelta
import pickle

import pytz
from dateutil import parser
import os.path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource
from typing import List, Dict

# If modifying these SCOPES, delete the file token1.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class MyCalendar:

    def google_calendar_auth(self):
        """
        Connects to the Google Calendar API and returns a service resource object.

        :return: A service resource object for interacting with the Google Calendar API.
        """
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}, re-authenticating...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)
        return service

    def create_event(self, start_time_str, summary, duration=1, description=None, location=None):
        service = self.google_calendar_auth()
        start_time = parser.parse(start_time_str)
        end_time = start_time + timedelta(hours=duration)

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {event.get('htmlLink')}")
        return event

    def get_events(self, n: int) -> List[Dict]:
        """
            Fetches upcoming events from the Google Calendar.

            :param service: The Google Calendar service resource object.
            :param n: Number of events to fetch.
            :return list of events
        """
        service = self.google_calendar_auth()
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming n events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=n, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        # Print events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        # save them to the file
        self.convert_events_to_string(events)

        return events

    def get_calendar_timezone(self, service, calendarId='primary'):
        """Fetch the timezone of the specified Google Calendar."""
        calendar = service.calendars().get(calendarId=calendarId).execute()
        return calendar['timeZone']

    def convert_events_to_string(self, events):
        if not events:
            return "No upcoming events found."

        event_strings = []
        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            end_time = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No Title')
            event_str = f"{summary}, from {start_time} to {end_time}"
            event_strings.append(event_str)
        with open("documents/schedule.txt", "w") as f:
            f.write("\n".join(event_strings))
        return "\n".join(event_strings)

    def get_events_from_to(self, start_date, end_date):
        service = self.google_calendar_auth()

        calendar_timezone = self.get_calendar_timezone(service, calendarId='primary')
        tz = pytz.timezone(calendar_timezone)

        # Convert start_date_str and end_date_str to datetime objects in the calendar's timezone
        start_date = tz.localize(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = tz.localize(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1))

        # Convert to RFC3339 format
        start_date = start_date.isoformat()
        end_date = end_date.isoformat()

        events_result = service.events().list(calendarId='primary', timeMin=start_date,
                                              timeMax=end_date, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
        return events

    def get_events_for_day(self, start_date):
        service = self.google_calendar_auth()

        if type(start_date) is str:
            start_datetime = parser.parse(start_date)

            # If you need just the date part and want to ignore the time and timezone
            start_date = start_datetime.date()

        calendar_timezone = self.get_calendar_timezone(service, calendarId='primary')
        tz = pytz.timezone(calendar_timezone)

        start_time = tz.localize(datetime.combine(start_date, datetime.min.time())).isoformat()
        end_time = tz.localize(datetime.combine(start_date, datetime.max.time())).isoformat()
        print("get_events_for_day is called for following dates: ")
        print(start_time)
        print(end_time)

        events_result = service.events().list(calendarId='primary', timeMin=start_time,
                                              timeMax=end_time, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(start, event['summary'])
        return events

    def get_events_n_days(self, n_days, start_date=None ):
        """Shows usage of the Google Calendar API. Prints the start and name of the next events."""
        service = self.google_calendar_auth()

        calendar_timezone = self.get_calendar_timezone(service, calendarId='primary')
        tz = pytz.timezone(calendar_timezone)

        if start_date is None:
            # Use today's date in the calendar's timezone
            start_date = datetime.now(tz).date()
        else:
            # Convert start_date_str to a date object
            start_datetime = parser.parse(start_date)

            # If you need just the date part and want to ignore the time and timezone
            start_date = start_datetime.date()

            # Localize the start datetime to the calendar's timezone
        start_datetime = tz.localize(datetime.combine(start_date, datetime.min.time()))

        # Calculate end datetime in the calendar's timezone
        end_datetime = tz.localize(datetime.combine(start_date, datetime.max.time()) + timedelta(days=n_days))

        start_time = start_datetime.isoformat()
        end_time = end_datetime.isoformat()

        print("here in calendar call")
        events_result = service.events().list(calendarId='primary', timeMin=start_time,
                                              timeMax=end_time, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

        # Process and return events
            # save them to the file
        self.convert_events_to_string(events)

        return events



if __name__ == '__main__':
    print("Welcome to PlanPal! ")
    c = MyCalendar()

    # c.create_event('2024-02-04T10:00:00', 'Meeting with Bob', 2, 'Discussing project progress',
    #                'Office')
    recent_events = c.get_events_n_days(2)
    # c.convert_events_to_string(recent_events)
    c.get_events_for_day('2024-02-23')
