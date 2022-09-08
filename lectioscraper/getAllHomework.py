from bs4 import BeautifulSoup
import json
import re
import logging


def get_all_homework(to_json, print_to_console, SchoolId, studentId, Session):
    HOMEWORK_URL = (
        "https://www.lectio.dk/lectio/{}/material_lektieoversigt.aspx?elevid={}".format(
            SchoolId, studentId
        )
    )
    homework = Session.get(HOMEWORK_URL)
    soup = BeautifulSoup(homework.text, features="html.parser")
    lektierows = soup.find("table", {"class": "ls-table-layout1"}).find_all("tr")
    lektier = {}
    for lektie in lektierows:
        lektieinfo = lektie.find("td", {"class": "ls-homework"})
        aktivitetcontainer = lektie.find_all("td", {"class": "textTop"})[0].find(
            "a", {"class": "s2bgbox"}
        )
        note = lektie.find_all("td", {"class": "textTop"})[1]
        rows = aktivitetcontainer["data-additionalinfo"].split("\n")
        timeStructure = re.compile(r"(\d+)/(\d+)-(\d+) (\d+):(\d+) til (\d+):(\d+)")
        teamStructure = re.compile("Hold: ")
        teacherStructure = re.compile("Lærer.*: ")
        roomStructure = re.compile("Lokale.*: ")
        if "absid" in aktivitetcontainer["href"]:
            lessonIdSplit1 = aktivitetcontainer["href"].split("absid=")
        elif "ProeveholdId" in aktivitetcontainer["href"]:
            lessonIdSplit1 = aktivitetcontainer["href"].split("ProeveholdId=")
        else:
            logging.warning("Error")
            return False
        lessonIdSplit2 = lessonIdSplit1[1].split("&prevurl=")
        lessonId = lessonIdSplit2[0]

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
        time_split = time.split(" ")
        lektier[team] = {
            "laerer": teacher,
            "title": title,
            "date": time_split[0],
            "note": note.text,
            "lektie": lektieinfo.text,
        }
    if len(lektier) == 0:
        return "No homework found"
    if to_json:
        with open("homework.json", "w") as f:
            json.dump(lektier, f, indent=4)
    if print_to_console:
        print(json.dumps(lektier, indent=4))
    return "Saved homework to homework.json" if to_json else lektier
