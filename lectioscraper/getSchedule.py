from bs4 import BeautifulSoup
import re
import logging
import json


def get_schedule(to_json, SchoolId, studentId, Session):
    SCHEDULE_URL = (
        "https://www.lectio.dk/lectio/"
        + SchoolId
        + "/SkemaNy.aspx?type=elev&elevid="
        + studentId
    )

    schedule = Session.get(SCHEDULE_URL)

    soup = BeautifulSoup(schedule.text, features="html.parser")
    # print(soup.prettify())

    scheduleContainer = soup.findAll("a", {"class": "s2bgbox"})

    Schedule = {}
    fullSchedule = {}
    # loop through the schedule and append the lessons to the fullSchedule list
    if scheduleContainer is None:
        logging.error("No schedule found")
        return False

    for schedule in scheduleContainer:
        rows = schedule["data-additionalinfo"].split("\n")
        timeStructure = re.compile(r"(\d+)/(\d+)-(\d+) (\d+):(\d+) til (\d+):(\d+)")
        teamStructure = re.compile("Hold: ")
        teacherStructure = re.compile("Lærer.*: ")
        roomStructure = re.compile("Lokale.*: ")

        # Getting the lesson id
        # Get the lesson if normal
        if "absid" in schedule["href"]:
            lessonIdSplit1 = schedule["href"].split("absid=")
        elif "ProeveholdId" in schedule["href"]:
            lessonIdSplit1 = schedule["href"].split("ProeveholdId=")
        else:
            logging.warning("Error")
            return False

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

        # If list is empty (There is no room or teacher) then make list empty
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
        if time != " ":
            Schedule["StartTime"] = time_split[1]
            Schedule["EndTime"] = time_split[3]
        else:
            Schedule["StartTime"] = " "
            Schedule["EndTime"] = " "
        
        Schedule["Team"] = team
        Schedule["Teacher"] = teacher
        Schedule["Room"] = room
        Schedule["Id"] = lessonId

        fullSchedule[Schedule["Id"]] = Schedule
        Schedule = {}
    if to_json:
        with open("schedule.json", "w") as f:
            json.dump(fullSchedule, f, indent=4)
    if len(fullSchedule) == 0:
        logging.error("No schedule found")
        return "No schedule found"
    return "saved in schedule.json" if to_json else fullSchedule
