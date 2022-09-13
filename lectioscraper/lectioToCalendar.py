import datetime
from email.policy import HTTP
import os
import json
import sched
from urllib.error import HTTPError
# import google calendar api
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests
from bs4 import BeautifulSoup
from lxml import html
import re

SCOPES = ['https://www.googleapis.com/auth/calendar']

class LecToCal:
    def __init__(self, Session, CalendarID, StudentId, SchoolId, schoolAddress, user_type):
        self.Session = Session
        self.CalendarID = CalendarID
        self.StudentId = StudentId
        self.SchoolId = SchoolId
        self.schoolAddress = schoolAddress
        self.user_type = user_type
        
    def getLectioSchema(self, weeks:int=1):
        current_week = datetime.datetime.now().isocalendar()[1]
        current_year = datetime.datetime.now().isocalendar()[0]
        
        
        absoluteSchedule = {}
        """
        format of schedule (for google calendar):
        {
            "date": {
                "start": "2020-10-01T08:00:00+02:00",
                "end": "2020-10-01T09:00:00+02:00",
                "summary": "Math",
                "description": "Math with Mr. Smith",
                "location": "Room 1"
            }
        }
        """
        for week in range(weeks):
            week = current_week + week
            fullSchedule = {}
            if week > 52:
                week = week - 52
                current_year = current_year + 1
            SCHEDULE_FOR_WEEK_URL = f"https://www.lectio.dk/lectio/{self.SchoolId}/SkemaNy.aspx?type={self.user_type}&{self.user_type}id={self.StudentId}&week={week}{current_year}"  # noqa: E501
            schedule_for_week = self.Session.get(SCHEDULE_FOR_WEEK_URL)
            soup = BeautifulSoup(schedule_for_week.text, features="html.parser")
            scheduleContainer = soup.findAll("a", {"class": "s2bgbox"})
            # if scheduleContainer is None skip week
            if len(scheduleContainer) == 0:
                print("No schedule for week " + str(week))
                # skip to next week
                continue
            
            for schedule in scheduleContainer:
                Schedule = {}
                rows = schedule["data-additionalinfo"].split("\n")
                timeStructure = re.compile(r"(\d+)/(\d+)-(\d+) (\d+):(\d+) til (\d+):(\d+)")
                teamStructure = re.compile("Hold: ")
                teacherStructure = re.compile("Lærer: ")
                roomStructure = re.compile("Lokale: ")
                # the important info for a google calendar event
                """
                1. start time
                2. end time
                3. summary
                4. description
                5. location
                6. date
                7. status aka. color
                
                """
                if "absid" in schedule["href"]:
                    lessonIdSplit1 = schedule["href"].split("absid=")
                elif "ProeveholdId" in schedule["href"]:
                    lessonIdSplit1 = schedule["href"].split("ProeveholdId=")
                    
                lessonIdSplit2 = lessonIdSplit1[1].split("&prevurl=")
                lessonId = lessonIdSplit2[0]
                
                # Check if there is a status
                if rows[0] == "Aflyst!" or rows[0] == "Ændret!":
                    # print("found a status: {}".format(rows[0]))

                    status = rows[0]

                    # Check if there is a title
                    if timeStructure.match(rows[1]):
                        # print("did not find a title")
                        title = " "
                    else:
                        # print("found a title: {}".format(rows[1]))
                        title = rows[1]

                else:
                    # print("did not find any status")
                    status = " "

                    # Check if there is a title
                    if timeStructure.match(rows[0]):
                        # print("did not find a title")
                        title = " "
                    else:
                        # print("found a title: {}".format(rows[0]))
                        title = rows[0]
                time = list(filter(timeStructure.match, rows))
                team = list(filter(teamStructure.match, rows))
                teacher = list(filter(teacherStructure.match, rows))
                room = list(filter(roomStructure.match, rows))

                if len(time) == 0:
                    time = " "
                else:
                    time = time[0]

                if len(team) == 0:
                    team = " "
                else:
                    team = team[0].split(":")[1].strip()

                if len(teacher) == 0:
                    teacher = " "
                else:
                    teacher = teacher[0].split(":")[1].strip()

                if len(room) == 0:
                    room = " "
                else:
                    room = room[0].split(":")[1].strip()

                # .split(":")[2]
                if time != " ":
                    time_split = time.split(" ")
                
                if status == "Aflyst!":
                    Schedule["Status"] = "Aflyst!"
                elif status == "Ændret!":
                    Schedule["Status"] = "Aendret!"
                else:
                    Schedule["Status"] = "Normal!"

                if title == " ":
                    Schedule["Title"] = "Ingen titel"
                else:
                    Schedule["Title"] = title

               
                    
                Schedule["DateTime"] = time
                Schedule["Date"] = time_split[0].replace("/", "-")
                Schedule["Date"] = str(datetime.datetime.strptime(Schedule["Date"], "%d-%m-%Y").date())
                # date should be in format 2020-10-01
                
                if time_split == " ":
                    Schedule["StartTime"] = " "
                    Schedule["EndTime"] = " "
                else:
                    Schedule["StartTime"] = time_split[1]
                    Schedule["EndTime"] = time_split[3]
                Schedule["Team"] = team
                Schedule["Teacher"] = teacher
                Schedule["Room"] = room
                Schedule["Id"] = lessonId
                # print(Schedule["Status"])
                if Schedule["Status"] == "Aflyst!":
                    # set color to red
                    Schedule["Color"] = 11
                elif Schedule["Status"] == "Aendret!":
                    # set color to yellow
                    Schedule["Color"] = 5
                elif Schedule["Status"] == "Normal!":
                    # set color to green
                    Schedule["Color"] = 10
                # add schedule to fullSchedule in a readable format for google calendar
                # timezone should be Europe/Copenhagen
                
                fullSchedule[Schedule["Id"]] = Schedule
                schedule = {}
                
                
            absoluteSchedule[week] = fullSchedule
            fullSchedule = {}
        
        
        return absoluteSchedule
    
    def format_schedule(self, weeks=1):
        """
        Makes the schedule ready to be sent to google calendar
        """
        schedule = self.getLectioSchema(12)
        formattedSchedule = {}
        """
        Schedule contains this format:
        {
            "weekNumber": {
                "date": {
                    "Status": "Normal!",
                    "Title": "Ingen titel",
                    "DateTime": "1/10-1 8:00 til 9:00",
                    "Date": "12-9-2022",
                    "StartTime": "8:00",
                    "EndTime": "9:00",
                    "Team": " ",
                    "Teacher": " ",
                    "Room": " ",
                    "Id": "123456",
            },
            etc...
                
        }
        format for google calendar:
        {
            "date": {
                "summary": "title",
                "description": "description",
                "location": "location",
                "start": {
                    "dateTime": "YYYY-MM-DDTHH:MM:SS.MMMZ",
                    "timeZone": "Europe/Copenhagen"
                },
                "end": {
                    "dateTime": "YYYY-MM-DDTHH:MM:SS.MMMZ",
                    "timeZone": "Europe/Copenhagen"
                },
                "colorId": 9
            },
        """
        for week in schedule:
            for date in schedule[week]:
                formattedSchedule[date] = {
                    "summary": schedule[week][date]["Team"],
                    "location": self.schoolAddress,
                    "description": "Test",# schedule[week][date]["DateTime"],
                    "start": {
                        # datetime currently looks like this: 12-9-2022T15:30:00+02:00 but it should look like this 2022-09-12T15:30:00+02:00 fix it
                        "dateTime": schedule[week][date]["Date"] + "T" + schedule[week][date]["StartTime"] + ":00+02:00",
                        "timeZone": "Europe/Copenhagen"
                    },
                    "end": {
                        "dateTime": schedule[week][date]["Date"] + "T" + schedule[week][date]["EndTime"] + ":00+02:00",
                        "timeZone": "Europe/Copenhagen"
                    },
                    "colorId": schedule[week][date]["Color"]
                }
        
        return formattedSchedule

    def send_to_google_calendar(self, weeks=1):
        """
        Sends the schedule to google calendar
        """
        # get the schedule
        schedule = self.format_schedule(weeks)
        calendarid = self.CalendarID
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        for id in schedule:
            try:
                service = build('calendar', 'v3', credentials=creds)

                # Call the Calendar API

                startTime = schedule[id]["start"]["dateTime"]
                endTime = schedule[id]["end"]["dateTime"]
                event = {
                    'summary': schedule[id]["summary"],
                    'location': schedule[id]["location"],
                    'description': schedule[id]["description"],
                    'start': {
                        'dateTime': startTime,
                        'timeZone': 'Europe/Copenhagen',
                    },
                    'end': {
                        'dateTime': endTime,
                        'timeZone': 'Europe/Copenhagen',
                    },
                    'colorId': schedule[id]["colorId"],
                }
                # check if there's already an event on that date and if True, update it
                events_result = service.events().list(calendarId=calendarid, timeMin=startTime, timeMax=endTime, singleEvents=True, orderBy='startTime').execute()
                events = events_result.get('items', [])
                if not events:
                    event = service.events().insert(calendarId=calendarid, body=event).execute()
                    print('Event created: %s' % (event.get('htmlLink')))
                else:
                    # get the event id
                    event = service.events().update(calendarId=calendarid, eventId=events[0]["id"], body=event).execute()
                    print('Event updated: %s' % (event.get('htmlLink')))
            except HTTPError as error:
                print('An error occurred: %s' % error)

        