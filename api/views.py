from urllib.error import HTTPError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from google_auth_oauthlib.flow import Flow
import os
import os.path
from googleapiclient.discovery import build
import datetime
import json

curr_directory = os.path.dirname(os.path.abspath(__file__))
creds_directory = os.path.join(curr_directory, 'credentials.json')
scopes=['https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile','https://www.googleapis.com/auth/calendar']

def index(request):
    return render(request, 'index.html')

def docs(request):
    return render(request, 'docs.html')

def about(request):
    return render(request, 'about.html')

# view for google oauth login to get access token of the user
def GoogleCalendarInitView(request):
    #Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = Flow.from_client_secrets_file(
        creds_directory,
        scopes)
    flow.redirect_uri='http://127.0.0.1:8000/rest/v1/calendar/redirect'
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')
    # Store the state in the session to verify that it is a
    # legitimate request from Google.
    request.session['state'] = state
    return redirect(authorization_url)

def GoogleCalendarRedirectView(request):
    # Specify the state when creating the flow in the callback so that it can verify
    # that the authorization server response is from Google.
    flow = Flow.from_client_secrets_file(
        creds_directory,
        scopes)
    authotization_response = request.get_full_path()
    token = flow.fetch_token(authorization_response=authotization_response)
    credentials = flow.credentials
    try:
        # get events from google calendars with credentials in sessions
        # Create an instance of the Calendar client
        service = build('calendar', 'v3', credentials=credentials)
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        events_results = service.events().list(calendarId='primary', timeMin=now,singleEvents=True,orderBy='startTime').execute()
        events = events_results.get('items', [])
        if not events:
            return HttpResponse({'message':'No upcoming events found.'})
        response_data={}
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            response_data[start]=event['summary']
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    except HTTPError as error:
        return HttpResponse({'message':error})


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }