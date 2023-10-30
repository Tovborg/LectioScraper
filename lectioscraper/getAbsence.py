from bs4 import BeautifulSoup
import json


def get_absence(to_json: bool, SchoolId: str, Session, written_assignments: bool):
    # The URL used for retrieving absence. Note: Might change over time
    ABSENCE_URL = "https://www.lectio.dk/lectio/{}/subnav/fravaerelev.aspx".format(SchoolId)
    
    absence = Session.get(ABSENCE_URL)
    soup = BeautifulSoup(absence.text, features="html.parser")
    absence_rows = soup.find(
        "table", {"id": "s_m_Content_Content_SFTabStudentAbsenceDataTable"}
    ).findAll("tr")

    absence_end_result = {}

    for i in absence_rows:
        data = i.findAll("td")
        absence = [j.text for j in data]
        # print(absence)
        if written_assignments is False:
            if len(absence) == 9:
                absence_end_result[absence[0]] = {
                    "team": absence[0],
                    "opgjort": {"procent": absence[1], "moduler": absence[2]},
                    "for_the_year": {"procent": absence[3], "moduler": absence[4]},
                }
        else:
            if len(absence) == 9:
                absence_end_result[absence[0]] = {
                    "team": absence[0],
                    "opgjort": {"procent": absence[1], "moduler": absence[2]},
                    "for_the_year": {"procent": absence[3], "moduler": absence[4]},
                    "writing": {
                        "opgjort": {"procent": absence[5], "elevtid": absence[6]},
                        "for_the_year_wrting": {
                            "procent": absence[7],
                            "elevtid": absence[8],
                        },
                    },
                }

    if to_json == True:
        with open("absence.json", "w") as outfile:
            json.dump(absence_end_result, outfile, indent=4)
    if len(absence_end_result) == 0:
        return "No absence found"

    return "Saved absence to absence.json" if to_json else absence_end_result
