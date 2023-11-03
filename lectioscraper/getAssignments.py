import json
from bs4 import BeautifulSoup
import logging
import re
# Exceptions
from lectioscraper.exceptions import ElementNotFoundError, RequestError, LectioLayoutChangeError

def get_assignments(save_to_json, SchoolId, Session):
    # Initiate session and soup
    ASSIGNMENTS_URL = "https://www.lectio.dk/lectio/{}/OpgaverElev.aspx".format(SchoolId)
    assignments = Session.get(ASSIGNMENTS_URL)
    if assignments.status_code != 200:
        raise RequestError(ASSIGNMENTS_URL)
    soup = BeautifulSoup(assignments.text, features="html.parser")
    
    assignments_table = soup.find("table", {"id": "s_m_Content_Content_ExerciseGV"})
    if assignments_table is None:
        raise ElementNotFoundError("table", "s_m_Content_Content_ExerciseGV")
    try:
        assignments_rows = assignments_table.find_all("tr")[1:]
    except IndexError:
        raise ElementNotFoundError("rows")

    assignments_json = {}
    for row in assignments_rows:
        link = f"https://www.lectio.dk{row.find('a', {'title': 'Gå til opgaveafleveringssiden'})['href']}"
        pattern = r"elevid=(\d+)&exerciseid=(\d+)&prevurl=([\w/.]+)"

        match = re.search(pattern, link)

        if match:
            elevid = match.group(1)
            exerciseid = match.group(2)
            prevurl = match.group(3)
        else:
            print("No match found.")
        
        payload = {
            "elevid": elevid,
            "exerciseid": exerciseid,
            "prevurl": prevurl
        }

        assignment_session = Session.get(link, data=payload)
        if assignment_session.status_code != 200:
            raise RequestError(link)
        assignment_soup = BeautifulSoup(assignment_session.text, features="html.parser")
        
        # Assignment information
        assignment_info = assignment_soup.find("table", {"class": "ls-std-table-inputlist"})
        if assignment_info is None:
            raise ElementNotFoundError("table", "ls-std-table-inputlist")

        # Assignment info cases
        opgavetitel = assignment_info.find("th", text = 'Opgavetitel:').find_next_sibling("td").text if "Opgavetitel:" in assignment_info.text else None
        opgavebeskrivelse = assignment_info.find("th", text = 'Opgavebeskrivelse:').find_next_sibling("td").text if "Opgavebeskrivelse:" in assignment_info.text else None
        opgavenote = assignment_info.find("th", text = 'Opgavenote:').find_next_sibling("td").text if "Opgavenote:" in assignment_info.text else None
        hold = assignment_info.find("th", text = 'Hold:').find_next_sibling("td").text if "Hold:" in assignment_info.text else None
        karakterskala = assignment_info.find("th", text = 'Karakterskala:').find_next_sibling("td").text if "Karakterskala:" in assignment_info.text else None
        ansvarlig = assignment_info.find("th", text = 'Ansvarlig:').find_next_sibling("td").text if "Ansvarlig:" in assignment_info.text else None
        afleveringsfrist = assignment_info.find("th", text = 'Afleveringsfrist:').find_next_sibling("td").text if "Afleveringsfrist:" in assignment_info.text else None
        i_undervisningsbeskrivelse = assignment_info.find("th", text = 'I undervisningsbeskrivelse:').find_next_sibling("td").text if "I undervisningsbeskrivelse:" in assignment_info.text else None

        afleverering_info = assignment_soup.find("div", {"id": "m_Content_ctl02_pa"})
        if afleverering_info is None:
            raise ElementNotFoundError("div", "m_Content_ctl02_pa")
        aflevering_info_table = afleverering_info.find("table", {"id": "m_Content_StudentGV"})
        if aflevering_info_table is None:
            raise ElementNotFoundError("table", "m_Content_StudentGV")
        try:
            aflevering_info_row = aflevering_info_table.find_all("tr")[1]
        except IndexError:
            raise ElementNotFoundError("rows")
        try:
            aflevering_info_data = aflevering_info_row.find_all("td")[1:]
        except IndexError:
            raise ElementNotFoundError("td")
        
        # Aflevering info
        try:
            elev = aflevering_info_data[0].text
            afventer = aflevering_info_data[1].text
            status = aflevering_info_data[2].text.split("/")[0].strip()
            fravaer = aflevering_info_data[2].text.split("/")[1].strip().split(" ")[1]
            karakter = aflevering_info_data[4].text
            karakternote = aflevering_info_data[5].text
            elevnote = aflevering_info_data[6].text
        except IndexError:
            raise LectioLayoutChangeError("absence")


        # Json insertion
        assignments_json[opgavetitel] = {
            "opgavebeskrivelse": opgavebeskrivelse,
            "opgavenote": opgavenote,
            "hold": hold,
            "karakterskala": karakterskala,
            "ansvarlig": ansvarlig,
            "afleveringsfrist": afleveringsfrist,
            "i_undervisningsbeskrivelse": i_undervisningsbeskrivelse,
            "elev": elev,
            "afventer": afventer,
            "status": status,
            "fravaer": fravaer,
            "karakter": karakter,
            "karakternote": karakternote,
            "elevnote": elevnote
        }
    if save_to_json:
        with open("assignments.json", "w") as f:
            json.dump(assignments_json, f, indent=4)
    return assignments_json
       
        
        


