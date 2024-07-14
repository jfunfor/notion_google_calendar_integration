from Notion import Notion
from GoogleCalendar import GoogleCalendar
import os
from datetime import datetime, timedelta

googleCalendarId = os.environ['GOOGLE_CALENDAR_ID']  # usually it would be an email
googleServiceAccountFile = 'svc.json'  # define filename from where get google calendar svc credentials
googleCalendarScopes = ['https://www.googleapis.com/auth/calendar']
notion_database_id = os.environ['NOTION_DATABASE_ID']  # get it from your database url in notion
notion_token = os.environ['NOTION_API_TOKEN']  # token, which is needed to connect to the notion API
notion_query_template = {  # filter query which is sent to notion api and is got only next month items
    'database_id': notion_database_id,
    'filter': {
        'property': 'Date',
        'date': {
            'on_or_after': f"{datetime.today()}"
        },
    },
}

# initialize notion and google calendar API clients
notion_client = Notion(notion_token)
google_client = GoogleCalendar(googleServiceAccountFile, googleCalendarScopes)

# get events from google calendar
google_calendar_events = google_client.get_event_list(googleCalendarId)

#  get items from notion database
notion_items = notion_client.get_query_db(notion_query_template)

#  check for changes in notion and delete them if events in notion don't match to google calendars'
for google_event in google_calendar_events:
    for notion_item in notion_items:
        #  if id in google event's description matches notion event id
        if google_event['description'] == notion_item['id']:
            if (
                    #  if event's start date, end date or name from Google calendar doesn't match notion's, delete it
                    google_event['start_date'] != notion_item['start_date'] or
                    google_event['name'] != notion_item['name'] or
                    google_event['end_date'] != notion_item['end_date']
            ):
                google_delete_id = google_client.delete_event(google_event['id'], googleCalendarId)
                print(f"Notion event deleted from google calendar!🤬 Look at details below: "
                      f"\n google event id: '{google_delete_id}'. "
                      f"\n notion event id: '{notion_item['id']}'. ")

print(' ')
print(' ')

#  add events from notion to google calendar
for notion_item in notion_items:
    #  if notion event is new and its id not in any of Google events' description
    if notion_item['id'] not in [google_event['description'] for google_event in google_calendar_events]:

        google_event_dict = google_client.make_event_dict(notion_item['name'],
                                                          notion_item['id'],
                                                          notion_item['start_date'],
                                                          notion_item['end_date'])
        google_create_id = google_client.create_event(google_event_dict, googleCalendarId)
        print(' ')
        print(f"Notion event added to google calendar!👽 Look at details below: "
              f"\n google event id: '{google_create_id}'. "
              f"\n notion event id: '{notion_item['id']}'. ")
    else:
        print(' ')
        print(f"Notion event id equals to google event description!😬 Look at details below: "
              f"\n notion id: '{notion_item['id']}'. ")
