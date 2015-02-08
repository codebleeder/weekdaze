__author__ = 'sharads'
import json

import flask
import httplib2

from apiclient import discovery
from oauth2client import client
from flask import jsonify, render_template

app = flask.Flask(__name__)


@app.route('/')
def index():
  if 'credentials' not in flask.session:
    return flask.redirect(flask.url_for('oauth2callback'))
    #return flask.render('index.html')
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    #drive_service = discovery.build('drive', 'v2', http_auth)
    calendar_service = discovery.build('calendar', 'v3', http_auth)
    #files = drive_service.files().list().execute()
    #return json.dumps(files)
    page_token = None
    # while True:
    #     events = calendar_service.events().list(calendarId='primary', pageToken=page_token).execute()
    #     for event in events['items']:
    #         return event['summary']
    #     page_token = events.get('nextPageToken')
    #     if not page_token:
    #         break
    events = calendar_service.events().list(calendarId='primary', pageToken=page_token).execute()
    with open('templates/gcal.json', 'w') as outfile:
        json.dump(events, outfile)
    #return jsonify(events)
    # eventList = []
    # while True:
    #     for event in events['items']:
    #         object = {
    #             'title': event['summary'],
    #             'start': event['start'],
    #             'end': event['end']
    #         }
    #         eventList.append(object)
    #     page_token = events.get('nextPageToken')
    #     if not page_token:
    #         break
    # return jsonify(eventList)
    return render_template('default.html', gcal_data=events)

@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      #scope='https://www.googleapis.com/auth/drive.metadata.readonly',
      scope='https://www.googleapis.com/auth/calendar',
      redirect_uri=flask.url_for('oauth2callback', _external=True))

  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = True
  app.run(host='0.0.0.0')

