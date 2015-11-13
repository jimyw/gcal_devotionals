from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import datetime
import secrets

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_Calendar_List(service):
    page_token = None
    while True:
      calendar_list = service.calendarList().list(pageToken=page_token).execute()
      for calendar_list_entry in calendar_list['items']:
        print(calendar_list_entry['summary'])
        # print(calendar_list_entry)
      page_token = calendar_list.get('nextPageToken')
      if not page_token:
        break

def create_Event(service, title, email, date):
    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/google-apps/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any stored credentials.

    event = {
      'summary': title,
      'description': 'Reminder for writing devos to OneBodyInChrist. You will receive an automatic calendar notification one day before you are scheduled to write (hopefully).',
      'start': {
        'date': date,
        # 'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'date': date,#'2015-10-19',
      },
      'attendees': [
        {'email': email},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},  # unfortunately, this notification is only set for the sender's calendar. Notifications for guests to the day-long events are set by default (by google) to email at 4:30pm day before and controlled by guests themselves
        ],
      },
    }

    # print(event)
    event = service.events().insert(calendarId=secrets.calendarID, body=event, sendNotifications=True).execute()
    # event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def create_OneBody_Event(service, start_date):
    f = open('names.txt')
    content = [x.strip('\n') for x in f.readlines()]
    t = start_date
    for line in content:
        temp = [x.strip() for x in line.split(',')]
        name = temp[0]
        email = temp[1]
        date = t.strftime('%Y-%m-%d')
        create_Event(service, name, email, date)
        # print(name, email, date)
        # print(email)
        t+=datetime.timedelta(days=1)   # add one day

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    # get_Calendar_List(service)  # get a list of calendars on this account
    create_OneBody_Event(service, datetime.datetime(2015,11,14,0,0))

    # create_Event(service,"testing notification", 'xxx@gmail.com', "2015-11-13")

if __name__ == '__main__':
    main()