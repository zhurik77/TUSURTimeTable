import requests
from bs4 import BeautifulSoup

# Send a GET request to the website URL
url = "https://timetable.tusur.ru/faculties/fb/groups/712-1?week_id=665"
response = requests.get(url)

# Get the HTML content
html_content = response.text

# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table element
table = soup.find('table', class_='table-lessons')

# Find all table rows within the table element
rows = table.find_all('tr')

# Loop through the rows
for row in rows:
    # Find the time span
    time_span = row.find('span', class_='time')
    if time_span:
        time = time_span.text.strip()
        print('Time:', time)

    # Find the lesson details
    lesson_details = row.find('div', class_='lesson-cell')
    if lesson_details:
        discipline = lesson_details.find('abbr', class_='js-tooltip').text.strip()
        kind = lesson_details.find('span', class_='kind').text.strip()
        auditoriums = lesson_details.find('span', class_='auditoriums').text.strip()
        teacher = lesson_details.find('span', class_='group').text.strip()

        print('Discipline:', discipline)
        print('Kind:', kind)
        print('Auditoriums:', auditoriums)
        print('Teacher:', teacher)

    print('---')