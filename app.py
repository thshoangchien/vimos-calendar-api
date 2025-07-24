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

def get_all_calendars(access_token):
    url = "https://www.googleapis.com/calendar/v3/users/me/calendarList"
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(url, headers=headers).json().get("items", [])

def fetch_events(access_token, start_time, end_time):
    calendars = get_all_calendars(access_token)
    headers = {"Authorization": f"Bearer {access_token}"}
    all_events = []
    for cal in calendars:
        cal_id = cal["id"]
        cal_name = cal.get("summary", "Lịch không tên")
        events_url = f"https://www.googleapis.com/calendar/v3/calendars/{cal_id}/events"
        params = {
            "timeMin": start_time,
            "timeMax": end_time,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        res = requests.get(events_url, headers=headers, params=params).json()
        for event in res.get("items", []):
            start_val = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", "")
            end_val = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date", "")
            if "date" in event.get("start", {}):
                start_val += " (Cả ngày)"
            all_events.append({
                "id": event.get("id"),
                "calendarId": cal_id,
                "calendar": cal_name,
                "summary": event.get("summary", "Không có tiêu đề"),
                "start": start_val,
                "end": end_val
            })
    return all_events

@app.route('/events/today', methods=['GET'])
def get_events_today():
    access_token = refresh_token()
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    start_time = tz.localize(datetime.now().replace(hour=0, minute=0)).isoformat()
    end_time = tz.localize(datetime.now().replace(hour=23, minute=59)).isoformat()
    return jsonify({"events": fetch_events(access_token, start_time, end_time)})

@app.route('/events/week', methods=['GET'])
def get_events_week():
    access_token = refresh_token()
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    start_time = tz.localize(datetime.now()).isoformat()
    end_time = tz.localize(datetime.now() + timedelta(days=7)).isoformat()
    return jsonify({"events": fetch_events(access_token, start_time, end_time)})

@app.route('/events/month', methods=['GET'])
def get_events_month():
    access_token = refresh_token()
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    start_time = tz.localize(datetime.now()).isoformat()
    end_time = tz.localize(datetime.now() + timedelta(days=30)).isoformat()
    return jsonify({"events": fetch_events(access_token, start_time, end_time)})

@app.route('/events/search', methods=['POST'])
def search_events():
    access_token = refresh_token()
    keyword = request.json.get("keyword", "").lower()
    tz = pytz.timezone("Asia/Ho_Chi_Minh")
    start_time = tz.localize(datetime.now()).isoformat()
    end_time = tz.localize(datetime.now() + timedelta(days=30)).isoformat()
    events = fetch_events(access_token, start_time, end_time)
    filtered = [e for e in events if keyword in e["summary"].lower()]
    return jsonify({"events": filtered})

@app.route('/events/delete', methods=['POST'])
def delete_event():
    access_token = refresh_token()
    event_id = request.json.get("id")
    calendar_id = request.json.get("calendarId", "primary")
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(url, headers=headers)
    return jsonify({"status": "deleted" if response.status_code == 204 else "failed"})

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
