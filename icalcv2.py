import requests
from icalendar import Calendar
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
import re

group_list = [
    "712-1", "712-2", "712-m", "722-1", "732-1", "742-1", "742-2", "762-1", "762-2",
    "711-1", "711-2", "721-1", "721-2", "731-1", "731-2", "741-1", "761-1",
    "710-1", "710-2", "720-1", "720-2", "730-1", "730-2", "740-1", "760-1",
    "719-1", "729-1", "739-1", "749-1", "769-1", "769-2", "738-1", "748"
]

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

def convert_to_24hr_format(timestamp):
    # Convert timestamp to 24-hour format
    return datetime.strftime(timestamp, "%H:%M")

def clean_room_name(room):
    # Remove any invalid characters from the room name
    return re.sub(r"[^\w\s-]", "", room)

used_rooms = []
teachers = []

all_timetables = []

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
            "Group": group,
            "Date": event.get("DTSTART").dt.date(),
            "Start Time": convert_to_24hr_format(event.get("DTSTART").dt),
            "End Time": convert_to_24hr_format(event.get("DTEND").dt),
            "Summary": event.get("SUMMARY"),
            "Location": event.get("LOCATION"),
            "Teacher": "",
        }
        # Extract teacher name from the event description
        description = event.get("DESCRIPTION")
        if description:
            teacher = description.split(", ")[1:]
            event_info["Teacher"] = ", ".join(teacher)
            if event_info["Teacher"] not in teachers:
                teachers.append(event_info["Teacher"])

        events.append(event_info)
        room = event_info["Location"]
        rooms = split_rooms(room)
        for r in rooms:
            if not is_room_duplicate(r, used_rooms):
                used_rooms.append(r)

    # Create a DataFrame from the extracted event information
    timetable = pd.DataFrame(events)

    # Convert the date and time columns to the desired format
    timetable["Date"] = pd.to_datetime(timetable["Date"]).dt.strftime("%d-%m-%Y")
    timetable["Time"] = timetable["Start Time"] + " - " + timetable["End Time"]

    # Reorder and select the desired columns
    timetable = timetable[["Group", "Date", "Time", "Summary", "Location", "Teacher"]]

    # Add the timetable DataFrame to the list
    all_timetables.append(timetable)

    # Write the group timetable to an HTML file
    group_file_name = f"{group}.html"
    group_file_path = os.path.join(folder_name, group_file_name)
    timetable.to_html(group_file_path, index=False, justify="center", encoding="utf-8-sig")

# Concatenate all the timetables into a single DataFrame
all_tables = pd.concat(all_timetables, ignore_index=True)

# Write the combined timetable to an HTML file
all_file_name = "all_groups.html"
all_file_path = os.path.join(folder_name, all_file_name)
all_tables.to_html(all_file_path, index=False, justify="center", encoding="utf-8-sig")

# Process room timetables
for room in used_rooms:
    # Clean the room name
    clean_room = clean_room_name(room)

    # Get the room timetable for all groups
    room_timetable = all_tables[all_tables["Location"].str.contains(room, case=False, na=False)]

    # Write the room timetable to an HTML file
    room_file_name = f"{clean_room}.html"
    room_file_path = os.path.join(folder_name, room_file_name)
    room_timetable.to_html(room_file_path, index=False, justify="center", encoding="utf-8-sig")

# Save the used rooms information
used_rooms_file = os.path.join(folder_name, "used_rooms.txt")
with open(used_rooms_file, "w", encoding="utf-8-sig") as file:
    file.write("\n".join(used_rooms))

# Save the teacher information
teachers_file = os.path.join(folder_name, "teachers.txt")
with open(teachers_file, "w", encoding="utf-8-sig") as file:
    file.write("\n".join(teachers))

print("Timetable extraction completed successfully!")
