from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

TOKEN_DATA = {
    "access_token": "ya29.a0AS3H6NwDcN82LUaIx8DPUwxth8NyVVDlBnHFfgE97ASV5a0obWcYJIBuJOeirI6nNIcQ2xW4Tu0QE6Blw31j_4mZ6obvB4puh0U8SEF8Zq8gIZZrdGU-k8dujgPtrNiIwFoBZTEdMMv2q8sJwCGZKIA1PDIZzpGZ2NTxXDXcaCgYKAWQSARQSFQHGX2MibK14Za5D9LDwH6qKQDeGLg0175",
    "refresh_token": "1//0eWyXtuzZOhUCCgYIARAAGA4SNwF-L9IrsYzg6QKFO9b-FLergjQJ-5KpUDG4_JUVgP0FyvG9wZYTso4qIvwW-qjhI1lup7VIu_E",
    "client_id": "345327211976-onbe4nr4a8mlr689s1ua1iso69bfogh2.apps.googleusercontent.com",
    "client_secret": "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",
    "token_uri": "https://oauth2.googleapis.com/token"
}

def refresh_token():
    url = TOKEN_DATA["token_uri"]
    payload = {
        "client_id": TOKEN_DATA["client_id"],
        "client_secret": TOKEN_DATA["client_secret"],
        "refresh_token": TOKEN_DATA["refresh_token"],
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload).json()
    if "access_token" in response:
        TOKEN_DATA["access_token"] = response["access_token"]
    return TOKEN_DATA["access_token"]

@app.route('/events/today', methods=['GET'])
def get_today_events():
    access_token = refresh_token()
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    start_time = tz.localize(datetime.now().replace(hour=0, minute=0, second=0)).isoformat()
    end_time = tz.localize(datetime.now().replace(hour=23, minute=59, second=59)).isoformat()

    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    params = {
        "timeMin": start_time,
        "timeMax": end_time,
        "singleEvents": "true",
        "orderBy": "startTime"
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, params=params).json()
    return jsonify(response)

@app.route('/events/create', methods=['POST'])
def create_event():
    access_token = refresh_token()
    data = request.json
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    event = {
        "summary": data.get("summary"),
        "start": {"dateTime": data.get("start"), "timeZone": "Asia/Ho_Chi_Minh"},
        "end": {"dateTime": data.get("end"), "timeZone": "Asia/Ho_Chi_Minh"}
    }
    response = requests.post(url, headers=headers, json=event).json()
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
