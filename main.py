import requests
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
load_dotenv()
# API call to get event data
url = "https://sgf-meetup-api.opensgf.org/events?group=open-sgf&next=true"
headers = {
    "Authorization": "Bearer " + os.getenv("security-keys")
}

response = requests.get(url, headers=headers)
# Check if the request was successful
if response.status_code == 200:
    data = response.json()

    # Check if there are any events
    if data['events']:
        # Convert the dateTime to CDT
        print(data['events'][0]['dateTime'])
        utc_time = datetime.strptime(data['events'][0]['dateTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_time = utc_time.replace(tzinfo=pytz.utc)
        cdt_time = utc_time.astimezone(pytz.timezone('America/Chicago'))

        # Prepare the embedded message
        event = data['events'][0]
        embed = { # Embed object
            "title": event['title'],
            "description": event['description'],
            "url": event['eventUrl'],
            "timestamp": cdt_time.isoformat(),
            "color": 5814783,  # Optional: color of the embed
            "fields": [# Array of field objects
                {"name": "Group", "value": event['group']['name'], "inline": True},
                {"name": "Host", "value": event['host']['name'], "inline": True},
                {"name": "Location", "value": f"{event['venue']['name']}, {event['venue']['address']}, {event['venue']['city']}, {event['venue']['state']} {event['venue']['postalCode']}", "inline": False},
                {"name": "Duration", "value": event['duration'], "inline": True},
                {"name": "Time", "value": cdt_time.strftime("%Y-%m-%d %I:%M:%S %p %Z"), "inline": True},
            ]
        }

        # Check if the event is more than 24 hours away
        if cdt_time < datetime.now(pytz.timezone('America/Chicago')) + timedelta(hours=24):
            webhook_url = os.getenv("url")
            payload = {
                "embeds": [embed]
            }

            # Send the webhook
            webhook_response = requests.post(webhook_url, json=payload)

            if webhook_response.status_code == 204:
                print("Webhook sent successfully")
            else:
                print(f"Failed to send webhook with status code {webhook_response.status_code}")
        else:
            print("Event is more than 24 hours away")
    else:
        print("No events found")
else:
    print(f"Request failed with status code {response.status_code}")