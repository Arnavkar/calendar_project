from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
import pytz
import os

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_user(calendar_id):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f'token_{calendar_id}.json'):
        creds = Credentials.from_authorized_user_file(f'token_{calendar_id}.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'token_{calendar_id}.json', 'w') as token:
            token.write(creds.to_json())
    assert(creds!=None)
    return creds


def get_busy_times_google(creds,calendar_id,start_time,end_time):
    # Define the scopes for the Google Calendar API
    try:
        # Set up the Calendar API service object
        service = build('calendar', 'v3', credentials=creds)

        # Define the request body for the free/busy query
        request_body = {
            'timeMin': start_time.isoformat(),
            'timeMax': end_time.isoformat(),
            'items': [{'id': calendar_id}],
            'timeZone':"EST"
        }
        # Call the free/busy query API
        freebusy = service.freebusy().query(body=request_body).execute()
        # Extract the free/busy information from the response
        calendars = freebusy['calendars']
        busy_time_list = calendars[calendar_id]['busy']
        return busy_time_list

    except HttpError as error:
        print(f'An error occurred: {error}')

def compute_free_times(busy_times,start_time,end_time):
    # Identify the free time slots
    busy_times.sort()
    free_periods = []
    last_end = start_time
    for busy_start, busy_end in busy_times:
        if last_end < busy_start:
            free_periods.append((last_end, busy_start))
        last_end = max(last_end, busy_end)
    if last_end < end_time:
        free_periods.append((last_end, end_time))

    print("FREE TIMES-------")
    for free_start, free_end in free_periods:
        print(f'{free_start.strftime("%x - %X")} to {free_end.strftime("%x - %X")}')

if __name__ == '__main__':
    calendar_ids = ['as9086@bard.edu', 'arnavshirodkar@gmail.com']
    tz = pytz.timezone("EST")
    start_time = datetime.now(tz)
    end_time = start_time + timedelta(days=1)
    busy_times = []
    for calendar_id in calendar_ids:
        creds = authenticate_user(calendar_id)
        for busy_time in get_busy_times_google(creds,calendar_id,start_time,end_time):
            start = datetime.fromisoformat(busy_time['start'])
            end = datetime.fromisoformat(busy_time['end'])
            busy_times.append((start, end))
    compute_free_times(busy_times,start_time,end_time)
    