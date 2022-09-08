from bs4 import BeautifulSoup
import json
import logging


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("lectioscraper")
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


def get_absence(to_json: bool, SchoolId, studentId, Session, written_assignments: bool):
    ABSENCE_URL = "https://www.lectio.dk/lectio/{}/subnav/fravaerelev.aspx?elevid={}&prevurl=forside.aspx".format(
        SchoolId, studentId
    )
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
