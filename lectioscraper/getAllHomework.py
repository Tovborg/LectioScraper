from bs4 import BeautifulSoup
import json
import re
import logging
from collections import defaultdict

def get_all_homework(to_json, SchoolId, Session):
    HOMEWORK_URL = "https://www.lectio.dk/lectio/{}/material_lektieoversigt.aspx".format(SchoolId)
    homework = Session.get(HOMEWORK_URL)
    soup = BeautifulSoup(homework.text, features="html.parser")

    homework_table = soup.find("div", {"id": "s_m_Content_Content_contentPnl"}).find("table")
    homework_rows = homework_table.find_all("tr")

    # Stores each value in a list fx. "fr 3/11": []
    homework_json = defaultdict(list)

    for homework in homework_rows:
        dato = homework.find("th").text
        data = homework.find_all("td")
        
        aktivitet = data[0].find("a")['data-additionalinfo']

        pattern = r'(Lektier|Note):\s+(.*?)(?=\n\n\w+:|\Z)'
        matches = re.findall(pattern, aktivitet, re.DOTALL)

        # Initialize variables for "Note" and "Lektier"
        Note = ''
        Lektier = ''

        # Extract the matched sections and store them in variables
        for match in matches:
            section_name, section_content = match
            if section_name == 'Note':
                Note = section_content.strip()
            elif section_name == 'Lektier':
                Lektier = section_content.strip()
        


        # Print the extracted "Note" and "Lektier"
        time_match = re.search(r'(\d+:\d+) - (\d+:\d+)', aktivitet)
        start_time, end_time = time_match.groups() if time_match else ('', '')

        team_match = re.search(r'Hold: (.+)', aktivitet)
        team = team_match.group(1) if team_match else ''

        teacher_match = re.search(r'Lærer: (.+)', aktivitet)
        teacher = teacher_match.group(1) if teacher_match else ''
  
        classroom_match = re.search(r'Lokale: (.+)', aktivitet)
        classroom = classroom_match.group(1) if classroom_match else ''
        
        title = homework.find("div", {"class": "s2skemabrikcontent"}).text
        
        homework = {
            title: {
                "title": title,
                "dato": dato,
                "hold": team,
                "lærer": teacher,
                "lokale": classroom,
                "start_tid": start_time,
                "slut_tid": end_time,
                "Note": Note,
                "Lektier": Lektier,
            }
        }
        homework_json[dato].append(homework)
        
    if to_json:
        with open("homework.json", "w") as hw:
            json.dump(homework_json, hw, indent=4)
    return homework_json


