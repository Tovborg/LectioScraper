import requests
from lxml import html
from bs4 import BeautifulSoup
import logging
import re

# import functions
from lectioscraper.getSchedule import get_schedule
from lectioscraper.getAbsence import get_absence
from lectioscraper.getAllHomework import get_all_homework
from lectioscraper.getAssignments import get_assignments
from lectioscraper.getTodaysSchedule import get_todays_schedule
from lectioscraper.getMessages import getMessages

# exceptions
from lectioscraper.exceptions import ElementNotFoundError, LoginError




# main class

class Lectio:
    def __init__(self, Username: str, Password: str, SchoolId: str):
        # * ? Finished refactoring for also being able to scrape teachers Lectio
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
        self.SchoolId = SchoolId
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
            # its either a valueerror or a server error
            # raise an error not only if the school id is wrong, but also if the server is down
            raise ValueError(
                "School ID is wrong or the server is down, please try again later."
            )
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

        # Regex for studentId
        elevId_pattern = re.compile(r'elevid=\d+')
        elevid_mathes = soup.find_all(href=elevId_pattern)
        if len(elevid_mathes) == 0:
            raise LoginError("Login failed, please check your username and password. Or the server is down.")
        
        elevid_values = [re.search(r'elevid=(\d+)', match['href']).group(1) for match in elevid_mathes]
        insitutionFind = soup.find("div", {"class": "ls-master-header-institution"})
        insitution = "  ".join(insitutionFind.text.split())
        
        # split insitution at year/next year with only 2 digits
        insitution = re.split(r"(\d{4}/\d{2})", insitution)[0]
        
        # remove one whitespace between the names
        insitution = insitution.replace("  ", " ")
        
        self.studentId = elevid_values[0]
        self.Session = session

    def getSchedule(self, save_to_json: bool, week:int=None, year:int=None):
        # NOTE: This works, but needs fine tuning
        # TODO: Make this function work for other weeks than the current week
        # TODO: Get more information about homework and notes
        # ! If you make any changes to this function, make sure it integrates with addToGoogleCalendar function
        """
        getSchedule gets the schedule for the current week. Currently only works for the current week. # noqa: E501

        :param save_to_json: If true, the schedule will be saved to a json file.
        :param week: The week number of the schedule you want to scrape.
        :param year: The year of the schedule you want to scrape.

        :return: returns the schedule for the current week unless else is specified. If save_to_json is true, the schedule will be saved to a json file called schedule.json.

        """

        return get_schedule(
            Session=self.Session,
            SchoolId=self.SchoolId,
            save_to_json=save_to_json,
            week=week,
            year=year,
        )

    def getAbsence(self, written_assignments: bool, save_to_json: bool):
        # NOTE: This works now
        # * ? Should I make this function work for teachers, since they can also see absence?
        # * ? I don't know how the layout is for teachers, so I don't know if it will work
        """
        getAbsence gets the absence for the student for the whole year. If writing is true, the function will also scrape your absence for written assignments. If to_json is true, the absence will be saved to a json file called absence.json. # noqa: E501

        :param written_assignments: if true, the absence for written assignments will be scraped.
        :param save_to_json: if true, the absence will be saved to a json file called absence.json

        :return: returns the absence for the student in different classes for the whole year.
        """
        return get_absence(
            Session=self.Session,
            SchoolId=self.SchoolId,
            written_assignments=written_assignments,
            save_to_json=save_to_json,
        )

    def getAllHomework(self, save_to_json: bool):
        # NOTE: Needs reimplementation but works
        # NOTE: The print_to_console parameter is not necessary, since you can just print the dictionary that is returned
        # * ? Should I make this function work for teachers, since they can also see homework?
        # ? I don't know how the layout is for teachers, so I don't know if it will work
        """
        getAllHomework scrapes all the homework in the 'lektier' tab, currently there are no filters but scrapes all the homework for all classes, basically scrapes all the homework data that there is on the tab. # noqa: E501

        :param save_to_json: if true, the homework will be saved to a json file called homework.json.

        :return: returns all the homework in the 'lektier' either as a json file or as a dictionary.

        """
        return get_all_homework(
            Session=self.Session,
            SchoolId=self.SchoolId,
            save_to_json=save_to_json
        )

    def getAssignments(
        self,
        save_to_json=False,
    ):
        # TODO: Add files and filters
        """
        getAssignments scrapes all your current assignments, in the "Afleveringer" tab, and saves them to a json file called assignments.json if save_to_json is true. else it just returns the assignments.json file
        
        :param save_to_json: if true, the assignments will be saved to a json file called assignments.json.

        :return: returns all the assignments in the 'afleveringer' either as a json file or as a dictionary.
        """
        return get_assignments(
            Session=self.Session,
            SchoolId=self.SchoolId,
            save_to_json=save_to_json
        )

    def getMessages(self, save_to_json: bool = False):
        # NOTE: This has been fixed
        # TODO: Make this function work for teachers  
        # * I'm assuming teachers layout is the same as students, so it should work
        """
        Returns the messages in the "Beskeder" tab. If save_to_json is true, the messages will be saved to a json file called messages.json. 

        :param save_to_json: If true, the messages will be saved to a json file.
        

        :return: Returns the unread messages for the current user, if get_content is true, the message body will be returned too
        """

        return getMessages(
            Session=self.Session,
            SchoolId=self.SchoolId,
            save_to_json=save_to_json,
        )
        



