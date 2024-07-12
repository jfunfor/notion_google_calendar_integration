from __future__ import print_function
from datetime import datetime, timedelta, timezone
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendar(object):

    #  connect to google calendar api
    def __init__(self, serviceAccountFile, scopes):
        credentials = service_account.Credentials.from_service_account_file(serviceAccountFile, scopes=scopes)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    #  body template for google calendar api requests
    def make_event_dict(self, name, description, startTime, endTime) -> dict:
        event = {
            'summary': name,
            'description': description,
            'start': {
                'dateTime': str(startTime),
            },
            'end': {
                'dateTime': str(endTime),
            }
        }
        return event

    #  get all google calendar events from now
    def get_event_list(self, calendarId) -> list:
        now = datetime.utcnow().isoformat() + 'Z'
        print(now)
        print('Getting the upcoming events')
        print(' ')
        events_result = self.service.events().list(calendarId=calendarId,
                                                   timeMin=now, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')

        #  result list conversion
        result_list = []
        for event in events:
            result_list.append({
                'start_date': event['start']['dateTime'],
                'end_date': event['end']['dateTime'],
                'name': event['summary'],
                'description': event['description'],
                'id': event['id']
            })
        return result_list

    def create_event(self, event, calendarId):
        e = self.service.events().insert(calendarId=calendarId,
                                         body=event).execute()
        print('Event created in Google calendar with id: %s' % (e.get('id')))

    def delete_event(self, eventId, calendarId):
        self.service.events().delete(calendarId=calendarId,
                                     eventId=eventId).execute()
        print('Event deleted in Google calendar with id: %s' % eventId)
