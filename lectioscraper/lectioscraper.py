import re
import requests
from lxml import html
from bs4 import BeautifulSoup
import json
import datetime
import os
import time
import pytz
from typing import *
import logging
from getSchedule import get_schedule
from getAbsence import get_absence
from getAllHomework import get_all_homework
from getAssignments import get_assignments

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
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
    def __init__(self, Username:str, Password:str, SchoolId:str):
        """
        Initializes the class with the username, password and school id.
        Init is not to be used directly, but is used when you create an instance of the class.
        
        :param Username: The username of the student.
        
        :param Password: The password of the student.
        
        :param SchoolId: The school id of the student.
        
        :return: Will return an error if the username, password or school id is not provided or if login fails.
        """
        self.Username = Username
        self.Password = Password
        self.SchoolId = str(SchoolId)
        initalized = False
        
        LOGIN_URL = "https://www.lectio.dk/lectio/{}/login.aspx".format(self.SchoolId)
        
        session = requests.Session()
        result = session.get(LOGIN_URL)
        tree = html.fromstring(result.text)
        authenticity_token = list(set(tree.xpath("//input[@name='__EVENTVALIDATION']/@value")))[0]
        # print(authenticity_token)

        payload = {
            "m$Content$username": self.Username,
            "m$Content$password": self.Password,
            "m$Content$passwordHidden": self.Password,
            "__EVENTVALIDATION": authenticity_token,
            "__EVENTTARGET": "m$Content$submitbtn2",
            "__EVENTARGUMENT": "",
            "masterfootervalue": "X1!ÆØÅ",
            "LectioPostbackId": ""
        }
        
        result = session.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
        dashboard = session.get("https://www.lectio.dk/lectio/" + self.SchoolId + "/forside.aspx")
        soup = BeautifulSoup(dashboard.text, features="html.parser")
        studentIdFind = soup.find("a", {"id": "s_m_HeaderContent_subnavigator_ctl01"}, href=True)
        # print(studentIdFind)
        # print(soup.prettify())    

        if (studentIdFind == None):
            logging.warning("Login failed")
            initalized = False
        else:
            self.studentId = (studentIdFind['href']).replace("/lectio/" + SchoolId + "/forside.aspx?elevid=", '')

            self.Session = session
            initalized = True
        
    def getSchedule(self, to_json:bool, print_to_console:bool=False):
        """
        getSchedule gets the schedule for the current week. Currently only works for the current week.

        :param to_json: If true, the schedule will be saved to a json file.

        :param print_to_console: If true, the schedule will be printed to the console.

        :return: if to_json is true, the schedule will be saved to a json file. If to_json is false, the schedule will be returned. If print_to_console is true, the schedule will be printed to the console.
        """
        
        return get_schedule(Session=self.Session, SchoolId=self.SchoolId, studentId=self.studentId, to_json=to_json)
                            
    
    def getAbsence(self, written_assignments:bool, to_json:bool):
        """
        getAbsence gets the absence for the student for the whole year. If writing is true, the function will also scrape your absence for written assignments. If to_json is true, the absence will be saved to a json file called absence.json.
        
        :param written_assignments: if true, the absence for written assignments will be scraped.
        :param to_json: if true, the absence will be saved to a json file called absence.json
        
        :return: returns the absence for the student in different classes for the whole year.
        """
        return get_absence(Session=self.Session, SchoolId=self.SchoolId, studentId=self.studentId, written_assignments=written_assignments, to_json=to_json)
        
    
    def getAllHomework(self, to_json:bool, print_to_console:bool):
        """
        getAllHomework scrapes all the homework in the 'lektier' tab, currently there are no filters but scrapes all the homework for all classes, basically scrapes all the homework data that there is on the tab.
    
        :param to_json: if true, the homework will be saved to a json file called homework.json.
        :param print_to_console: if true, the homework will be printed to the console.
        
        :return: returns all the homework in the 'lektier' either as a json file or as a dictionary.
    
        """
        return get_all_homework(Session=self.Session, SchoolId=self.SchoolId, studentId=self.studentId, to_json=to_json, print_to_console=print_to_console)
        
    def getAssignments(self, to_json=False, team="alle hold", status="alle status", fravaer="", karakter=""):
        """
        getAssignments scrapes all your current assignments, this function actually has filters implemented so you can filter the assignments you want to see. Make sure to use the correct filters, otherwise you will get all the assignments.
        
        :param to_json: if true, the assignments will be saved to a json file called assignments.json.
        :param team: the team you want to filter the assignments by. Example: 1g/3 EnB (english with team 1g/3), the filters will be updated soon as it's complicated atm.
        :param status: the status you want to filter the assignments by. Example: Venter, Afleveret, Mangler
        :param fravaer: the absence you want to filter the assignments by. Example: 100% fravær, 50% fravær, 0% fravær
        :param karakter: the grade you want to filter the assignments by. Example: 12, 10, 7, 4, 02, 00, -3

        :return: returns all the assignments in the 'afleveringer' either as a json file or as a dictionary.
        """
        return get_assignments(Session=self.Session, SchoolId=self.SchoolId, studentId=self.studentId, to_json=to_json, team=team, status=status, fravaer=fravaer, karakter=karakter)
    
    def getTodaysSchedule(self, to_json=False):
        """
        Returns the schedule for the current day, the current day is found using the datetime module, working on choosing the next day if the current school day is over.
    
        :param to_json: If true, the schedule will be saved to a json file.
        
        :return: The schedule for the current day.
        """
        todays_schedule = {}
        date_today = datetime.date.today()
        schedule = self.getSchedule(to_json=False, print_to_console=False)
        # print(schedule)
        for i in schedule:
            
            date = i["Date"]
            # convert date to datetime object
            date = date.replace("/", "-")
            date = datetime.datetime.strptime(date, "%d-%m-%Y")
            # remove time from date
            date = date.date()
            if date == date_today:
                # add todays schedule to dictionary
                todays_schedule[i["Id"]] = i
        
        
                
        if len(todays_schedule) == 0:
            logging.info('No schedule found for today')
            return "No schedule found for today"
        
        
       
        if to_json is False:
            return todays_schedule
        elif to_json is True:
            with open('todays_schedule.json', 'w') as outfile:
                json.dump(todays_schedule, outfile, indent=4)
            return schedule
        else:
            logging.warning('Please only provide boolean value for to_json')
            return "Please only provide boolean value for to_json"
    
    def getUnreadMessages(self, to_json=False, get_content=False):
        """
        Returns the unread messages for the current user.
        
        :param to_json: If true, the messages will be saved to a json file.
        :param get_content: If true, the content of the messages will be returned aka the message body.
        
        :return: Returns the unread messages for the current user, if get_content is true, the message body will be returned too
        """
        
        messages = self.Session.get("https://www.lectio.dk/lectio/{}/beskeder2.aspx?type=&elevid={}&selectedfolderid=-70".format(self.SchoolId, self.studentId))
        soup = BeautifulSoup(messages.text, "html.parser")
        unread_messages = soup.find_all("tr", {"class": "unread"})
        if len(unread_messages) == 0:
            logging.info('No unread messages found')
            return None
        else:
            unr_messages = {}
            for i in unread_messages:
                td = i.find_all("td")
                useful_data = []
                for j in td:
                    if j.text != "":
                        useful_data.append(j.text.strip("\n"))
                
        
                if get_content is False:
                    
                    unr_messages[useful_data[0]] = {
                        "title": useful_data[0],
                        "latest_message_sender": useful_data[1],
                        "first_message_sender": useful_data[2],
                        "to": useful_data[3],
                        "day_and_date": useful_data[4],
                        "date": useful_data[4][3::]
                    }
                elif get_content is True:
                    postback_id = i.find("div", {"class": "buttonlink"}).find("a")["onclick"].split("'")[3].split("_")[3]
                    url = "https://www.lectio.dk/lectio/{}/beskeder2.aspx?type=showthread&elevid={}&selectedfolderid=-70&id={}".format(self.SchoolId, self.studentId, postback_id)
                    content = self.Session.get(url)
                    content_soup = BeautifulSoup(content.text, "html.parser")
                    tables = content_soup.find("table", {"class": "ShowMessageRecipients"})
                    recipient_rows = tables.findAll("tr")
                    emne = recipient_rows[0].find("td", {"class": "textLeft"}).text
                    emne = " ".join(emne.split())
                    full_table = content_soup.find("table", {"class": "maxW showmessage2", "id": "printmessagearea"})
                    recipient_table = full_table.find("table", {"class": "ShowMessageRecipients"})
                    # only get the two first rows, the rest is the message
                    recipient_rows = recipient_table.findAll("tr")[:3]
                    afsender_tabel = recipient_rows[2].find("table", {"class": "maxWidth textTop"})
                    afsender = afsender_tabel.findAll("tr")[0].find("span").text
                    til = afsender_tabel.findAll("tr")[1].findAll("td")[2].text
                    til = " ".join(til.split())
                    message = full_table.find("ul", {"id": "s_m_Content_Content_ThreadList"}).find("div").text
                    # convert all the danish characters to english
                    message = message.replace("æ", "ae")
                    message = message.replace("ø", "oe")
                    message = message.replace("å", "aa")
                    message = message.replace("Æ", "Ae")
                    message = message.replace("Ø", "Oe")
                    message = message.replace("Å", "Aa")
                    message = message.replace("æ", "ae")
                    message = message.replace("ø", "oe")
                    message = message.replace("å", "aa")
                    message = message.replace("Æ", "Ae")
                    message = message.replace("Ø", "Oe")
                    message = message.replace("Å", "Aa")
                    message = message.strip("\n")
                    message = message.strip("\r")
                
                
                    unr_messages[useful_data[0]] = {
                        "title": emne,
                        "latest_message_sender": useful_data[1],
                        "sender": afsender,
                        "to": til,
                        "content": message,
                        "day_and_date": useful_data[4],
                        "date": useful_data[4][3::]
                    }

            
            
            if to_json is False:
                return unr_messages
            else:
                with open('unread_messages.json', 'w') as outfile:
                    json.dump(unr_messages, outfile, indent=4)
                return unr_messages


            
    

client = Lectio("emil763x", "xf96G?YteTYqEA#A", "59")
client.getAssignments(to_json=True, team="1g/3 MaB")