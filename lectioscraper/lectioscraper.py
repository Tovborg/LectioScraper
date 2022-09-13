import requests
from lxml import html
from bs4 import BeautifulSoup
import logging
from lectioscraper.getSchedule import get_schedule
from lectioscraper.getAbsence import get_absence
from lectioscraper.getAllHomework import get_all_homework
from lectioscraper.getAssignments import get_assignments
from lectioscraper.getTodaysSchedule import get_todays_schedule
from lectioscraper.getUnreadMessages import get_unread_messages
import re
from lectioscraper.lectioToCalendar import LecToCal
class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"  # noqa: E501

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


class Lectio:
    def __init__(self, Username: str, Password: str, SchoolId: str):
        """
        Initializes the class with the username, password and school id. # noqa: E501
        Init is not to be used directly, but is used when you create an instance of the class.

        :param Username: The username of the student.

        :param Password: The password of the student.

        :param SchoolId: The school id of the student.

        :return: Will return an error if the username, password or school id is not provided or if login fails.
        """
        self.Username = Username
        self.Password = Password
        self.SchoolId = str(SchoolId)

        LOGIN_URL = "https://www.lectio.dk/lectio/{}/login.aspx".format(
            self.SchoolId
        )  # noqa: E501

        session = requests.Session()
        result = session.get(LOGIN_URL)
        tree = html.fromstring(result.text)
        try:

            authenticity_token = list(
                set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value"))
            )[0]
        except IndexError:
            logger.warning(
                "Failed to get authenticity token, please check your school id or it's a bug in either lectioscraper or lectio, try again later or contact me"  # noqa: E501
            )
            # create an exit that wont break django or flask

        # print(authenticity_token)

        payload = {
            "m$Content$username": self.Username,
            "m$Content$password": self.Password,
            "m$Content$passwordHidden": self.Password,
            "__EVENTVALIDATION": authenticity_token,
            "__EVENTTARGET": "m$Content$submitbtn2",
            "__EVENTARGUMENT": "",
            "masterfootervalue": "X1!ÆØÅ",
            "LectioPostbackId": "",
        }

        result = session.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))  # noqa: E501
        dashboard = session.get(
            "https://www.lectio.dk/lectio/" + self.SchoolId + "/forside.aspx"
        )
        soup = BeautifulSoup(dashboard.text, features="html.parser")
        insitutionFind = soup.find("div", {"class": "ls-master-header-institution"})
        insitution = "  ".join(insitutionFind.text.split())
        # split insitution at year/next year with only 2 digits
        insitution = re.split(r"(\d{4}/\d{2})", insitution)[0]
        # remove one whitespace between the names
        insitution = insitution.replace("  ", " ")
        
        # use google maps api to get the location of the school
        # get the location of the school
        maps_api_key = "AIzaSyAYrJzW_kIagSRVKIxmxbrmVI6W1T4W6jw"
        res = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(insitution, maps_api_key)).json()["results"][0]
        self.InstitutionAddress = res["formatted_address"]
        studentIdFind = soup.find(
            "a", {"id": "s_m_HeaderContent_subnavigator_ctl01"}, href=True
        )
        # print(studentIdFind)
        # print(soup.prettify())

        if studentIdFind is None:
            logger.error(
                "Login failed, please check your username and password"
            )  # noqa: E501
        else:
            self.studentId = (studentIdFind["href"]).replace(
                "/lectio/" + SchoolId + "/forside.aspx?elevid=", ""
            )
            self.Session = session

    def getSchedule(self, to_json: bool, print_to_console: bool = False):
        """
        getSchedule gets the schedule for the current week. Currently only works for the current week. # noqa: E501

        :param to_json: If true, the schedule will be saved to a json file.

        :param print_to_console: If true, the schedule will be printed to the console.

        :return: if to_json is true, the schedule will be saved to a json file. If to_json is false, the schedule will be returned. If print_to_console is true, the schedule will be printed to the console.
        """

        return get_schedule(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            to_json=to_json,
        )

    def getAbsence(self, written_assignments: bool, to_json: bool):
        """
        getAbsence gets the absence for the student for the whole year. If writing is true, the function will also scrape your absence for written assignments. If to_json is true, the absence will be saved to a json file called absence.json. # noqa: E501

        :param written_assignments: if true, the absence for written assignments will be scraped.
        :param to_json: if true, the absence will be saved to a json file called absence.json

        :return: returns the absence for the student in different classes for the whole year.
        """
        return get_absence(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            written_assignments=written_assignments,
            to_json=to_json,
        )

    def getAllHomework(self, to_json: bool, print_to_console: bool):
        """
        getAllHomework scrapes all the homework in the 'lektier' tab, currently there are no filters but scrapes all the homework for all classes, basically scrapes all the homework data that there is on the tab. # noqa: E501

        :param to_json: if true, the homework will be saved to a json file called homework.json.
        :param print_to_console: if true, the homework will be printed to the console.

        :return: returns all the homework in the 'lektier' either as a json file or as a dictionary.

        """
        return get_all_homework(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            to_json=to_json,
            print_to_console=print_to_console,
        )

    def getAssignments(
        self,
        to_json=False,
        team="alle hold",
        status="alle status",
        fravaer="",
        karakter="",
    ):
        """
        getAssignments scrapes all your current assignments, this function actually has filters implemented so you can filter the assignments you want to see. Make sure to use the correct filters, otherwise you will get all the assignments. # noqa: E501

        :param to_json: if true, the assignments will be saved to a json file called assignments.json.
        :param team: the team you want to filter the assignments by. Example: 1g/3 EnB (english with team 1g/3), the filters will be updated soon as it's complicated atm.
        :param status: the status you want to filter the assignments by. Example: Venter, Afleveret, Mangler
        :param fravaer: the absence you want to filter the assignments by. Example: 100% fravær, 50% fravær, 0% fravær
        :param karakter: the grade you want to filter the assignments by. Example: 12, 10, 7, 4, 02, 00, -3

        :return: returns all the assignments in the 'afleveringer' either as a json file or as a dictionary.
        """
        return get_assignments(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            to_json=to_json,
            team=team,
            status=status,
            fravaer=fravaer,
            karakter=karakter,
        )

    def getTodaysSchedule(self, to_json=False):
        """
        Returns the schedule for the current day, the current day is found using the datetime module, working on choosing the next day if the current school day is over. # noqa: E501

        :param to_json: If true, the schedule will be saved to a json file.

        :return: The schedule for the current day.
        """
        return get_todays_schedule(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            to_json=to_json,
        )

    def getUnreadMessages(self, to_json=False, get_content=False):
        """
        Returns the unread messages for the current user. # noqa: E501

        :param to_json: If true, the messages will be saved to a json file.
        :param get_content: If true, the content of the messages will be returned aka the message body.

        :return: Returns the unread messages for the current user, if get_content is true, the message body will be returned too
        """

        return get_unread_messages(
            Session=self.Session,
            SchoolId=self.SchoolId,
            studentId=self.studentId,
            to_json=to_json,
            get_content=get_content,
        )
        
    def addToGoogleCalendar(self, CalendarID:str, user_type:str):
        """
        Adds the schedule for the current week to a Google Calendar. # noqa: E501

        :param CalendarID: The ID of the calendar you want to add the schedule to.
        :param user_type: The type of user, either 'student' or 'teacher'.

        :return: Returns the schedule for the current week.
        """
        return LecToCal(self.Session, CalendarID, self.studentId, self.SchoolId, self.InstitutionAddress, user_type).send_to_google_calendar(12)


