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


class Lectio:
    def __init__(self, Username:str, Password:str, SchoolId:str):
        """
        Initializes the class with the username, password and school id.
        Init is not made to be used directly, but is used when you create an instance of the class.
        
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
            
            # print("Student id: " + self.studentId)
            # print("School id: " + self.SchoolId)

    def getSchedule(self, to_json:bool, print_to_console:bool=False):
        """
        getSchedule gets the schedule for the current week. Currently only works for the current week.

        :param to_json: If true, the schedule will be saved to a json file.

        :param print_to_console: If true, the schedule will be printed to the console.

        :return: if to_json is true, the schedule will be saved to a json file. If to_json is false, the schedule will be returned. If print_to_console is true, the schedule will be printed to the console.
        """

        SCHEDULE_URL = "https://www.lectio.dk/lectio/" + self.SchoolId + "/SkemaNy.aspx?type=elev&elevid=" + self.studentId

        schedule = self.Session.get(SCHEDULE_URL)

        soup = BeautifulSoup(schedule.text, features="html.parser")
        # print(soup.prettify())

        scheduleContainer = soup.findAll('a', {"class": "s2bgbox"})

        fullSchedule = []
        Schedule = {}

        # loop through the schedule and append the lessons to the fullSchedule list
        if (scheduleContainer != None):
            for schedule in scheduleContainer:
                rows = schedule['data-additionalinfo'].split("\n")
                timeStructure = re.compile(
                    r'(\d+)/(\d+)-(\d+) (\d+):(\d+) til (\d+):(\d+)')
                teamStructure = re.compile('Hold: ')
                teacherStructure = re.compile('Lærer.*: ')
                roomStructure = re.compile('Lokale.*: ')

                #Getting the lesson id
                # Get the lesson if normal
                if "absid" in schedule['href']:
                    lessonIdSplit1 = schedule['href'].split("absid=")
                elif "ProeveholdId" in schedule['href']:
                    lessonIdSplit1 = schedule['href'].split("ProeveholdId=")
                else:
                    logging.warning('Error')
                    return False
                
                lessonIdSplit2 = lessonIdSplit1[1].split("&prevurl=")
                lessonId = lessonIdSplit2[0]
                
                
                #Check if there is a status
                if rows[0] == "Aflyst!" or rows[0] == "Ændret!":
                    #print("found a status: {}".format(rows[0]))

                    status = rows[0]

                    #Check if there is a title
                    if timeStructure.match(rows[1]):
                        #print("did not find a title")
                        title = " "
                    else:
                        #print("found a title: {}".format(rows[1]))
                        title = rows[1]

                else:
                    #print("did not find any status")
                    status = " "

                    #Check if there is a title
                    if timeStructure.match(rows[0]):
                        #print("did not find a title")
                        title = " "
                    else:
                        #print("found a title: {}".format(rows[0]))
                        title = rows[0]

                time = list(filter(timeStructure.match, rows))
                team = list(filter(teamStructure.match, rows))
                teacher = list(filter(teacherStructure.match, rows))
                room = list(filter(roomStructure.match, rows))

                #If list is empty (There is no room or teacher) then make list empty
                if len(time) == 0:
                    time = " "
                else:
                    time = time[0]
                
                if len(team) == 0:
                    team = " "
                else:
                    team = team[0].split(":")[1].strip()
                
                if len(teacher) == 0:
                    teacher = " "
                else:
                    teacher = teacher[0].split(":")[1].strip()
                
                if len(room) == 0:
                    room = " "
                else:
                    room = room[0].split(":")[1].strip()

                #.split(":")[2]
                time_split = time.split(" ")
                
                if status == "Aflyst!":
                    Schedule['Status'] = "Aflyst!"
                elif status == "Ændret!":
                    Schedule['Status'] = "Aendret!"
                else:
                    Schedule['Status'] = "Normal!"
                    
                if title == " ":
                    Schedule['Title'] = "Ingen titel"
                else:
                    Schedule['Title'] = title
                    
                Schedule['DateTime'] = time
                Schedule['Date'] = time_split[0].replace("/", "-")
                Schedule['StartTime'] = time_split[1]
                Schedule['EndTime'] = time_split[3]
                Schedule['Team'] = team
                Schedule['Teacher'] = teacher
                Schedule['Room'] = room
                Schedule['Id'] = lessonId
                


                fullSchedule.append(Schedule)
                Schedule = {}

                
                #DEBUG PURPOSES
                """
                print(time[0])
                print(team[0])
                print(teacher[0])
                print(room[0])
                
                print("---------------------------")"""

            
            
            if to_json == True:
                # if a json file called schedule.json exists, it will be overwritten, if not it will be created
                with open('schedule.json', 'w') as outfile:
                    json_schedule = {}
                    for lesson in fullSchedule:
                        json_schedule[lesson['Id']] = lesson
                    json.dump(json_schedule, outfile, indent=4)

            elif to_json == False:
                if print_to_console == True:
                    logging.info("Schedule not saved, but it will be returned (print it to log it to the console)")
                    return fullSchedule
                else:
                    return fullSchedule
            else:
                logging.warning("Please only provide boolean values in the to_json parameter")
                return None
        else:
            logging.warning("No schedule found, please check your login details or see the readme")
            boolean = False
        return fullSchedule
            
            
        
        
        

        
        
    
    def getAbsence(self, written_assignments:bool, to_json:bool):
        """
        getAbsence gets the absence for the student for the whole year. If writing is true, the function will also scrape your absence for written assignments. If to_json is true, the absence will be saved to a json file called absence.json.
        
        :param written_assignments: if true, the absence for written assignments will be scraped.
        :param to_json: if true, the absence will be saved to a json file called absence.json
        
        :return: returns the absence for the student in different classes for the whole year.
        """

        if type(to_json) is not bool:
            logging.warning('to_json parameter must be a boolean')
            return "to_json parameter must be a boolean"
        if type(written_assignments) is not bool:
            logging.warning('written_assignments parameter must be a boolean')
            return "Must be a boolean"
        ABSENCE_URL = "https://www.lectio.dk/lectio/{}/subnav/fravaerelev.aspx?elevid={}&prevurl=forside.aspx".format(self.SchoolId, self.studentId)
        absence = self.Session.get(ABSENCE_URL)
        soup = BeautifulSoup(absence.text, features="html.parser")
        absence_table = soup.find("table", {"id": "s_m_Content_Content_SFTabStudentAbsenceDataTable"})
        absence_rows = absence_table.findAll("tr")

    
    
        
        absence_end_result = []
        
        for i in absence_rows:
            data = i.findAll("td")
            absence = []
            for j in data:
                absence.append(j.text)
            # print(absence)
            if written_assignments is False:
                if len(absence) == 9:
                    absence_end_result.append({"team": absence[0], "opgjort": {"procent": absence[1], "moduler": absence[2]}, "for_the_year": {"procent": absence[3], "moduler": absence[4]}})
            else:
                if len(absence) == 9:

                    absence_end_result.append({"team": absence[0], "opgjort": {"procent": absence[1], "moduler": absence[2]}, "for_the_year": {"procent": absence[3], "moduler": absence[4]}, "writing": {"opgjort": {"procent": absence[5], "elevtid": absence[6]}, "for_the_year_wrting": {"procent": absence[7], "elevtid": absence[8]}}})
            
        if to_json == True:
            with open('absence.json', 'w') as outfile:
                json.dump(absence_end_result, outfile, indent=4)
        elif to_json == False:
            logging.info("Absence not saved, but it will be returned (print it to log it to the console)")
            return absence_end_result
        else:
            logging.warning("Please only provide boolean values in the to_json parameter")
            return "to_json parameter must be a boolean"
        return absence_end_result
    
    def getAllHomework(self, to_json:bool, print_to_console:bool):
        """
        getAllHomework scrapes all the homework in the 'lektier' tab, currently there are no filters but scrapes all the homework for all classes, basically scrapes all the homework data that there is on the tab.
    
        :param to_json: if true, the homework will be saved to a json file called homework.json.
        :param print_to_console: if true, the homework will be printed to the console.
        
        :return: returns all the homework in the 'lektier' either as a json file or as a dictionary.
    
        """
        HOMEWORK_URL = "https://www.lectio.dk/lectio/{}/material_lektieoversigt.aspx?elevid={}".format(self.SchoolId, self.studentId)
        homework = self.Session.get(HOMEWORK_URL)
        soup = BeautifulSoup(homework.text, features="html.parser")
        homework_table_div = soup.find("div", {"class": "ls-content"})
        
        table = soup.find("table", {"class": "ls-table-layout1"})
        rows = table.findAll("tr")
        homework_end_result = {}
        
        for i in rows:
            date = i.find("th", {"class": "nowrap textTop"}).text
            scheduleContainer = i.find('a', {"class": "s2bgbox"})
            rows = scheduleContainer['data-additionalinfo'].split("\n")     
            note = i.find_all('td', {"class": "textTop"})
            for j in note:
                if j.text != "":
                    note = j.text
                else:
                    note = " "
            # print(note)
            
            ls_homework = i.find("td", {"class": "ls-homework"})
            # print(ls_homework.text)
            time_split = rows[1].split(" ")
            Homework = {
                "modul": rows[0],
                "date-and-time": rows[1],
                "dato_for_modul": time_split[0].replace("/", "-"),
                "startTid_for_modul": time_split[1],
                "slutTid_for_modul": time_split[-1],
                "hold": rows[2],
                "teacher": rows[3],
                "note": note,
                "lektie": ls_homework.text
            }
            homework_end_result[rows[2].strip("Hold: ")] = Homework
            
        if to_json is False:
            if print_to_console is True:
                for i in homework_end_result:
                    # print it in readable format
                    print("Modul: {}".format(i['modul']))
                    print("Date and time: {}".format(i['date-and-time']))
                    print("Hold: {}".format(i['hold']))
                    print("Teacher: {}".format(i['teacher']))
                    print("Note: {}".format(i['note']))
                    print("Lektie: {}".format(i['lektie']))
                    print("---------------------------")
            return homework_end_result
            
        else:
            with open('homework.json', 'w') as outfile:
                json.dump(homework_end_result, outfile, indent=4)
            return homework_end_result
        
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
        ASSIGNMENT_URL = "https://www.lectio.dk/lectio/{}/OpgaverElev.aspx?elevid={}".format(self.SchoolId, self.studentId)
        assignments = self.Session.get(ASSIGNMENT_URL)
        soup = BeautifulSoup(assignments.text, features="html.parser")
        assignment_table = soup.find("table", {"class": "ls-table-layout1 maxW textTop lf-grid"})
        assignment_rows_with_headers = assignment_table.findAll("tr")
        assignment_rows = assignment_rows_with_headers[1:]
        assignment_end_result = [] 
        for i in assignment_rows:
            td = i.findAll("td")
            assignment = []
            for j in td:
                assignment.append(j.text)
            assignment_dict = {
                "uge": assignment[0],
                "hold": assignment[1],
                "opgavetitel": assignment[2].strip("\n"),
                "frist": assignment[3],
                "tid": assignment[3][-5:],
                "elevtid": assignment[4],
                "status": assignment[5],
                "fravaer": assignment[6],
                "afventer": assignment[7],
                "opgavenote": assignment[8],
                "karakter": assignment[9],
                "elevnote": assignment[10],
            }
            
            assignment_end_result.append(assignment_dict)
    
        def filterAssignments(assignment_end_result, team, status, fravaer, karakter=""):
            filtered_assignments = {}
            for i in assignment_end_result:
                if team != "alle hold" and status != "alle status" and fravaer != "" and karakter != "":
                    if i["hold"] == team and i["status"] == status and i["fravaer"] == fravaer and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status != "alle status" and fravaer != "" and karakter == "":
                    if i["hold"] == team and i["status"] == status and i["fravaer"] == fravaer:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status != "alle status" and fravaer == "" and karakter != "":
                    if i["hold"] == team and i["status"] == status and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status != "alle status" and fravaer == "" and karakter == "":
                    if i["hold"] == team and i["status"] == status:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status == "alle status" and fravaer != "" and karakter != "":
                    if i["hold"] == team and i["fravaer"] == fravaer and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status == "alle status" and fravaer != "" and karakter == "":
                    if i["hold"] == team and i["fravaer"] == fravaer:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status == "alle status" and fravaer == "" and karakter != "":
                    if i["hold"] == team and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team != "alle hold" and status == "alle status" and fravaer == "" and karakter == "":
                    if i["hold"] == team:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status != "alle status" and fravaer != "" and karakter != "":
                    if i["status"] == status and i["fravaer"] == fravaer and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status != "alle status" and fravaer != "" and karakter == "":
                    if i["status"] == status and i["fravaer"] == fravaer:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status != "alle status" and fravaer == "" and karakter != "":
                    if i["status"] == status and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status != "alle status" and fravaer == "" and karakter == "":
                    if i["status"] == status:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status == "alle status" and fravaer != "" and karakter != "":
                    if i["fravaer"] == fravaer and i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status == "alle status" and fravaer != "" and karakter == "":
                    if i["fravaer"] == fravaer:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status == "alle status" and fravaer == "" and karakter != "":
                    if i["karakter"] == karakter:
                        filtered_assignments[i["opgavetitel"]] = i
                elif team == "alle hold" and status == "alle status" and fravaer == "" and karakter == "":
                    filtered_assignments[i["opgavetitel"]] = i
            # print(len(filtered_assignments))
            if len(filtered_assignments) == 0:
                logging.info('No assignments found with the given filters, please check your filters')
                return "No assignments found with the given filters, please check your filters"
            else:
                if to_json is False:
                    return filtered_assignments
                else:
                    with open('assignments.json', 'w') as outfile:
                        json.dump(filtered_assignments, outfile, indent=4)
                    return filtered_assignments
        
        return filterAssignments(assignment_end_result, team, status, fravaer, karakter)
    
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


            
    

