from bs4 import BeautifulSoup
import json
import re
import logging
from collections import defaultdict

# Exceptions
from lectioscraper.exceptions import ElementNotFoundError, RequestError

def get_all_homework(save_to_json, SchoolId, Session):
    # NOTE: Might change in the future
    HOMEWORK_URL = "https://www.lectio.dk/lectio/{}/material_lektieoversigt.aspx".format(SchoolId)

    homework = Session.get(HOMEWORK_URL)
    if homework.status_code != 200:
        raise RequestError(HOMEWORK_URL)
    soup = BeautifulSoup(homework.text, features="html.parser")
    if soup is None:
        raise ElementNotFoundError("soup")

    # Finds the table containing all the homework
    homework_table = soup.find("table", {"id": "s_m_Content_Content_MaterialLektieOverblikGV"})
    if homework_table is None:
        raise ElementNotFoundError("table", "s_m_Content_Content_MaterialLektieOverblikGV")

    # Stores each row in a list
    try:
        homework_rows = homework_table.find_all("tr")[1:]
    except IndexError:
        raise ElementNotFoundError("rows")
        
    # Stores each value in a list fx. "fr 3/11": []
    homework_json = defaultdict(list)

    # Loops through each row, scrapes and saves the data to a dictionary
    for homework in homework_rows:
        
        data = homework.find_all("td")
        if len(data) == 0:
            raise ElementNotFoundError("table data")
        dato = data[0].text
        aktivitet = data[1].find("a")['data-additionalinfo']
        
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
                
        time_match = re.search(r'(\d+:\d+) - (\d+:\d+)', aktivitet)
        start_time, end_time = time_match.groups() if time_match else ('', '')

        team_match = re.search(r'Hold: (.+)', aktivitet)
        team = team_match.group(1) if team_match else ''

        teacher_match = re.search(r'Lærer: (.+)', aktivitet)
        teacher = teacher_match.group(1) if teacher_match else ''
  
        classroom_match = re.search(r'Lokale: (.+)', aktivitet)
        classroom = classroom_match.group(1) if classroom_match else ''
        
        title_div = homework.find("div", {"class": "s2skemabrikcontent"})
        if title_div is None:
            raise ElementNotFoundError("div", "s2skemabrikcontent")
        title = title_div.text.strip()
        
        
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
        
    if save_to_json:
        with open("homework.json", "w") as hw:
            json.dump(homework_json, hw, indent=4)
    return homework_json


