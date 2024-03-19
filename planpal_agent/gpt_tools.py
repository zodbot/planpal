import json
import struct
from datetime import datetime
from typing import List

from my_calendar import MyCalendar

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_events",
            "description": "Add multiple events to my Google Calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "start_time": {
                                    "type": "string",
                                    "format": "date-time"
                                },
                                "summary": {
                                    "type": "string"
                                },
                                "duration": {
                                    "type": "integer"
                                },
                                "description": {
                                    "type": "string"
                                },
                                "location": {
                                    "type": "string"
                                }
                            },
                            "required": ["start_time", "summary", "duration"]
                        }
                    }
                },
                "required": ["events"]
            }
        }

    }
    ,

    {"type": "function",
     "function": {
         "name": "create_event",
         "description": "Add an event to my Google Calendar",
         "parameters": {
             "type": "object",
             "properties": {
                 "start_time": {
                     "type": "string",
                     "format": "date-time",
                     "description": "The start time of the event in ISO 8601 format, e.g., '2024-01-10T09:00:00'"
                 },
                 "summary": {
                     "type": "string",
                     "description": "A brief description or title of the event, e.g., 'Team Meeting'"
                 },
                 "duration": {
                     "type": "integer",
                     "description": "Duration of the event in hours, e.g., 2"
                 },
                 "description": {
                     "type": "string",
                     "description": "Detailed description of the event, e.g., 'Discussing project progress'"
                 },
                 "location": {
                     "type": "string",
                     "description": "Location of the event, e.g., 'Office' or 'San Francisco, CA'"
                 }
             },
             "required": ["start_time", "summary", "duration"]
         }
     }
     },
    {
        "type": "function",
        "function": {
            "name": "get_events",
            "description": "Retrieves a set number of upcoming events from Google "
                           "Calendar for specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "date to fetch events."
                    }
                },
                "required": ["start_date"]
            }
            # "description": "A list of events, each represented as an object."
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_events_n_days",
            "description": "Retrieves events for the specified number of upcoming "
                           "days",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of events to fetch."
                    }
                },
                "required": ["n"]
            }
            # "description": "A list of events, each represented as an object."
        }
    },

    {
        "type": "function",
        "function": {
            "name": "find_empty_slots",
            "description": "Finds empty time slots between events in Google Calendar within a specified date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date_str": {
                        "type": "string",
                        "format": "date",
                        "description": "The start date of the period to search for empty slots, in 'YYYY-MM-DD' format."
                    },
                    "end_date_str": {
                        "type": "string",
                        "format": "date",
                        "description": "The end date of the period to search for empty slots, in 'YYYY-MM-DD' format."
                    }
                },
                "required": ["start_date_str", "end_date_str"]
            }
        }
    }


]


class Event:
    start_time = datetime(2024, 1, 10, 9, 0, 0),
    summary = "Team Meeting",
    duration = 2,
    description = "Discussing project progress",
    location = "Office"


def get_calendar_events(start_date):
    c = MyCalendar()
    print("called get_calendar_events function! ")
    events = c.get_events_for_day(start_date=start_date)
    return json.dumps({"events": events})


def get_calendar_events_n_days(n_days):
    c = MyCalendar()
    print("called get_calendar_events function! ")
    events = c.get_events_n_days(n_days)
    return json.dumps({"events": events})


def create_calendar_event(start_time, summary, duration=1, description=None, location=None):
    c = MyCalendar()
    details = c.create_event(start_time, summary, duration, description, location)
    print("called create_calendar_event function! ")
    return json.dumps({"details": details})


def find_empty_slots(start_time, end_time):
    c = MyCalendar()
    empty_slots = c.find_empty_slots(start_time, end_time)
    return json.dumps({"empty_slots": empty_slots})


def create_multiple_calendar_events(events: List[Event]):
    c = MyCalendar()
    details = []
    for event in events:
        details.append(
            c.create_event(event.start_time, event.summary, event.duration, event.description, event.location))
    print("called create_calendar_event function! ")
    return json.dumps({"details": details})


available_functions = {
    "get_events": get_calendar_events,
    "get_events_n_days": get_calendar_events_n_days,
    "create_event": create_calendar_event,
    "create_events": create_multiple_calendar_events,
    "find_empty_slots": find_empty_slots
}


def function_call(function_name, function_args):
    function_response = ""
    function_to_call = available_functions[function_name]
    print("about to call function: ", function_to_call)
    if function_name == 'get_events':
        # Extract 'n' parameter for get_events function
        start_date = function_args.get("start_date")
        function_response = function_to_call(start_date=start_date)
        print(function_response)

    elif function_name == 'get_events_n_days':
        # Extract 'n' parameter for get_events function
        n = function_args.get("n")
        function_response = function_to_call(n_days=n)
        print(function_response)

    elif function_name == 'create_event':
        # Extract parameters for add_event function
        start_time = function_args.get("start_time")
        summary = function_args.get("summary")
        duration = function_args.get("duration")
        description = function_args.get("description")
        location = function_args.get("location")

        function_response = function_to_call(
            start_time=start_time,
            summary=summary,
            duration=duration,
            description=description,
            location=location
        )
    elif function_name == 'find_empty_slots':
        # Extract parameters for find_empty_slots method
        start_date_str = function_args.get("start_date_str")
        end_date_str = function_args.get("end_date_str")

        function_response = function_to_call(
            start_time=start_date_str,
            end_time=end_date_str
        )

        # print(function_response)

    elif function_name == 'create_events':
        events = function_args.get("events", [])
        function_responses = ""
        # Extract parameters for add_event function
        events_to_call = []
        for event in events:
            e = Event()
            e.start_time = event.get("start_time")
            e.summary = event.get("summary")
            e.duration = event.get("duration")
            e.description = event.get("description", "")  # Assuming description is optional
            e.location = event.get("location", "")
            events_to_call.append(e)
        function_response = function_to_call(events_to_call)
        # print(function_response)
    return function_response
