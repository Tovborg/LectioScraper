from bs4 import BeautifulSoup
from lectioscraper.getSchedule import get_schedule
import json
import re
import datetime


def get_todays_schedule(to_json, Session, SchoolId, studentId):
    date_today = datetime.date.today()
    schedule = get_schedule(
        to_json=False, Session=Session, SchoolId=SchoolId, studentId=studentId
    )
    todays_schedule = {
        i: schedule[i]
        for i in schedule
        if datetime.datetime.strptime(
            schedule[i]["Date"].replace("/", "-"), "%d-%m-%Y"
        ).date()
        == date_today
    }
    if len(todays_schedule) == 0:
        return "No schedule found for today"
    if to_json:
        with open("todaysSchedule.json", "w") as f:
            json.dump(todays_schedule, f, indent=4)
    return (
        "Saved todays schedule to todaysSchedule.json" if to_json else todays_schedule
    )
