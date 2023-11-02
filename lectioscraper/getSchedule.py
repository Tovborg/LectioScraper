from bs4 import BeautifulSoup
import re
import logging
import json
# Get current year
from datetime import datetime
from collections import defaultdict

def get_schedule(save_to_json:bool, SchoolId, Session, year:int=None, week:int=None):

    if year is None:
        year = str(datetime.now().year)
    # Get current week number
    print(year)
    if week is None:
        week = str(datetime.now().isocalendar()[1])
    print(week)

    SCHEDULE_URL = "https://www.lectio.dk/lectio/{}/SkemaNy.aspx?week={}{}".format(SchoolId, week, year)

    schedule = Session.get(SCHEDULE_URL)

    soup = BeautifulSoup(schedule.text, features="html.parser")

    day_rows = soup.find_all("div", {"class": "s2skemabrikcontainer lec-context-menu-instance"})
    date_rows = soup.find("tr", {"class": "s2dayHeader"})
    dates = [date.text.strip() for date in date_rows.find_all("td")][1:] # remove first element
    print(dates)

    # Create a dict with lists as values
    schedule = defaultdict(list)

    for index, day_row in enumerate(day_rows):
        skemabrikker = day_row.find_all("a", {"class": "s2skemabrik"})

        skema = defaultdict(list)
        
        for brik in skemabrikker:
            
            input_string = brik['data-additionalinfo']
            if "Lokale:" in input_string:
                lokale_pattern = r"Lokale: (.+)"
            elif "Lokaler:" in input_string:
                lokale_pattern = r"Lokaler: (.+)"
            status_pattern = r"(Ændret!|Aflyst!|normal)"

            modul_pattern = r"(\d{2}:\d{2} - \d{2}:\d{2})"
            hold_pattern = r"Hold: (.+)"
            lærer_pattern = r"Lærer: (.+)"

            ressource_pattern = r"Resource: (.+)"
            lektier_pattern = r"Lektier:(.+?)(?:Øvrigt indhold:|Note:|$)"
            øvrigt_indhold_pattern = r"Øvrigt indhold:(.+?)(?:Note:|$)"
            note_pattern = r"Note:(.+)$"

            # Anvend regex mønstrene på teksten
            status_match = re.search(status_pattern, input_string)
            modul_match = re.search(modul_pattern, input_string)
            lokale_match = re.search(lokale_pattern, input_string)
            hold_match = re.search(hold_pattern, input_string)
            lærer_match = re.search(lærer_pattern, input_string)
            lokale_match = re.search(lokale_pattern, input_string)

            ressource_match = re.search(ressource_pattern, input_string)
            lektier_match = re.search(lektier_pattern, input_string, re.MULTILINE | re.DOTALL)
            øvrigt_indhold_match = re.search(øvrigt_indhold_pattern, input_string, re.DOTALL)
            note_match = re.search(note_pattern, input_string, re.DOTALL)

            # Uddrag de matchede værdier
            status = status_match.group(1) if status_match else "normal"
            modul_start, modul_slut = modul_match.group().split(" - ") if modul_match else (None, None)
            hold = hold_match.group(1) if hold_match else None
            lærer = lærer_match.group(1) if lærer_match else None
            lokale = lokale_match.group(1) if lokale_match else None
            ressource = ressource_match.group(1) if ressource_match else None
            lektier = lektier_match.group(1).strip() if lektier_match else None
            øvrigt_indhold = øvrigt_indhold_match.group(1).strip() if øvrigt_indhold_match else None
            note = note_match.group(1).strip() if note_match else None

            result = hold.split(", ")
            for team2 in result:
                if "Alle" in team2:
                    # skip
                    members = []
                else:
                    a_tag = soup.find('a', text=str(team2))
                    if a_tag is None:
                        print("Not part of team " + team2)
                    else:
                        href_value = a_tag.get('href')
                        match = re.search(r'holdelementid=(\d+)', href_value)
                        if match:
                            extracted_value = match.group(1)
                        else:
                            return "ERROR: holdelementid not found"

                        schedule2 = Session.get("https://www.lectio.dk/lectio/{}/subnav/members.aspx?holdelementid={}&showteachers=1&showstudents=1".format(SchoolId, extracted_value))
                        soup2 = BeautifulSoup(schedule2.text, features="html.parser")
                        table = soup2.find("table", id="s_m_Content_Content_laerereleverpanel_alm_gv")
                        rows = table.findAll("tr")
                        rows.pop(0)
                        members = []
                        for row in rows: #for each member
                            memberinfo = row.findAll("td")
                            image = memberinfo[0].find("img", title="Vis større foto")
                            image = image.get('src')
                            def filter_by_id(tag):
                                return tag.has_attr('id') and 's_m_Content_Content_laerereleverpanel_alm_gv_ct' in tag['id']
                            def check_and_append(lst, obj):
                                for element in lst:
                                    if element == obj:
                                        return
                                lst.append(obj)
                            name = memberinfo[3].find(filter_by_id)
                            last_name = memberinfo[4].find("span", class_="noWrap")
                            teacher_or_student = memberinfo[1]
                            check_and_append(members, {
                                "image": "https://lectio.dk" + str(image),
                                "full_name": name.text + " " + last_name.text,
                                "type": teacher_or_student.text
                            })
                
            # check if a class with the same team already exists in the schedule
            modul = {
                hold: {
                    "status": status,
                    "start_time": modul_start,
                    "end_time": modul_slut,
                    "teacher": lærer,
                    "classroom": lokale,
                    "homework": lektier,
                    "note": note,
                    "oevrigt_indhold": øvrigt_indhold,
                    "ressource": ressource,
                    "members": members
                }
            }
            skema[dates[index]].append(modul)
        schedule[str(week)+"-"+str(year)].append(skema)
    if save_to_json:
        with open('schedule.json', 'w') as fp:
            json.dump(schedule, fp, indent=4)
    return schedule
    


    
        
        
        