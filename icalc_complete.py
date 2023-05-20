import requests
from icalendar import Calendar
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os

group_list = ["712-1", "712-2", "712-m", "722-1", "732-1", "742-1", "742-2", "762-1", "762-2"]

# Create a folder with the timestamp and current time appended
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
folder_name = f"{timestamp}_parce"
os.makedirs(folder_name, exist_ok=True)

def split_rooms(room):
    # Split the room string by comma and remove leading/trailing whitespaces
    return [r.strip() for r in room.split(",")]

def is_room_duplicate(room, used_rooms):
    # Check if the room already exists in the used_rooms array
    return room in used_rooms

used_rooms = []

# Load existing room entries from used_rooms.txt if it exists
used_rooms_file = os.path.join(folder_name, "used_rooms.txt")
if os.path.exists(used_rooms_file):
    with open(used_rooms_file, "r", encoding="utf-8-sig") as file:
        used_rooms = file.read().splitlines()

for group in group_list:
    # Generate the URL for the group
    url = f"https://timetable.tusur.ru/faculties/fb/groups/{group}.ics"

    # Send a GET request to the URL and get the iCalendar data
    response = requests.get(url)
    ical_data = response.text

    # Parse the iCalendar data
    cal = Calendar.from_ical(ical_data)

    # Extract relevant event information from the iCalendar data
    events = []
    for event in cal.walk("VEVENT"):
        event_info = {
            "Summary": event.get("SUMMARY"),
            "Location": event.get("LOCATION"),
            "Start Time": event.get("DTSTART").dt,
            "End Time": event.get("DTEND").dt
        }
        events.append(event_info)
        room = event_info["Location"]
        rooms = split_rooms(room)
        for r in rooms:
            if not is_room_duplicate(r, used_rooms):
                used_rooms.append(r)

    # Create a DataFrame for the group's timetable
    timetable = pd.DataFrame(events)

    # Create an HTML table from the timetable
    html_table = timetable.to_html(index=False)

    # Save the HTML table in a file
    file_name = f"{group}_timetable.html"
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, "w", encoding="utf-8-sig") as file:
        file.write(html_table)

    print(f"Saved {file_name} in {folder_name}")

# Save used room information in a separate file without duplicates
with open(used_rooms_file, "w", encoding="utf-8-sig") as file:
    for room in used_rooms:
        file.write(room + "\n")

print("Saved used_rooms.txt")
