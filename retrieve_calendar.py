from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta
import pytz

# Define the scopes for the Google Calendar API
scopes = ['https://www.googleapis.com/auth/calendar.readonly']

# Set up the credentials flow
flow = InstalledAppFlow.from_client_secrets_file('secret.json', scopes)

# Obtain the user's authorization
creds = flow.run_local_server(port=0)

calendar_ids = ['as9086@bard.edu', 'hm1795@bard.edu']

# Set up the Calendar API service object
service = build('calendar', 'v3', credentials=creds)

# Define the start and end times for the time range you want to check for free slots
start_time = datetime.now(pytz.utc)
end_time = start_time + timedelta(days=7)

# Define the time range in the format expected by the free/busy query
time_range = {
    'timeMin': start_time.isoformat(),
    'timeMax': end_time.isoformat(),
    'timeZone': 'UTC',
}

# Define the request body for the free/busy query
request_body = {
    'timeMin': start_time.isoformat(),
    'timeMax': end_time.isoformat(),
    'timeZone': 'UTC',
    'items': [{'id': calendar_id} for calendar_id in calendar_ids],
    'calendarExpansionMax': len(calendar_ids),
    'groupExpansionMax': len(calendar_ids),
    'freeBusyView': 'BUSY',
}

try:
    # Call the free/busy query API
    freebusy = service.freebusy().query(body=request_body).execute()
    print(freebusy)
    # Extract the free/busy information from the response
    calendars = freebusy['calendars']
    busy_times = [set(calendars[calendar_id]['busy']) for calendar_id in calendars]

    # Compute the free time slots by finding the intersection of the busy times
    # and the time range, and then subtracting the busy times from the time range
    free_times = set()
    for i in range(int((end_time-start_time).total_seconds()/1800)):
        free_times.add(start_time + timedelta(minutes=30)*i)

    print("BUSY TIMES-----")
    # print(busy_times)

    print("FREE TIMES-----")
    # print(free_times)

    for busy_set in busy_times:
        free_times = free_times - busy_set

    # Print the free time slots
    # print("Free Time Slots:")
    # for free_time in sorted(list(free_times)):
    #     print(free_time.astimezone(pytz.timezone('US/Pacific')).strftime('%m/%d/%Y %I:%M %p %Z'))

except HttpError as error:
    print(f'An error occurred: {error}')