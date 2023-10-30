
import logging
from bs4 import BeautifulSoup
import json
import re


def getMessages(SchoolId, Session, save_to_json: bool = False):
    # Needs new implementation after major Lectio update
    MESSAGE_URL = "https://www.lectio.dk/lectio/{}/beskeder2.aspx?mappeid=-70".format(SchoolId)
    unread_messages_session = Session.get(MESSAGE_URL)
    soup = BeautifulSoup(unread_messages_session.text, features="html.parser")

    # Asp.net hidden fields
    __VIEWSTATEX = soup.find("input", {"id": "__VIEWSTATEX"})["value"]
    __LASTFOCUS = None
    __SCROLLPOSITION = {"tableId":"","rowIndex":-1,"rowScreenOffsetTop":-1,"rowScreenOffsetLeft":-1,"pixelScrollTop":0,"pixelScrollLeft":0}
    __VIEWSTATEY_KEY = soup.find("input", {"id": "__VIEWSTATEY_KEY"})["value"]
    __VIEWSTATE = None
    __SCROLLPOSITIONX = 0
    __SCROLLPOSITIONY = 0
    __VIEWSTATEENCRYPTED = soup.find("input", {"id": "__VIEWSTATEENCRYPTED"})["value"]
    # Messages table
    messages_table = soup.find("table", {"class": "ls-table-layout5 highlightarea mobil-tråd-oversigt lf-grid"})
    # find all table rows but don't include the first one
    messages_rows = messages_table.findAll("tr")[1:]
    messages_json = {} 
    for message in messages_rows:
        
        td = message.findAll("td")
        topic_div = td[3]
        buttonlink = topic_div.find("a")["onclick"]
        pattern = r"__doPostBack\('(.*?)','(.*?)'\);"

        # Use re.search to find the matches
        match = re.search(pattern, buttonlink)

        if match:
            __EVENTTARGET = match.group(1)  # This will contain '__Page'
            __EVENTARGUMENT = match.group(2)  # This will contain the postback value
        else:
            print("No __EVENTTARGET or __EVENTARGUMENT found")
        
        payload = {
            "time": 0,
            "__EVENTTARGET": __EVENTTARGET,
            "__EVENTARGUMENT": __EVENTARGUMENT,
            "__LASTFOCUS": __LASTFOCUS,
            "__SCROLLPOSITION": __SCROLLPOSITION,
            "__VIEWSTATEX": __VIEWSTATEX,
            "__VIEWSTATEY_KEY": __VIEWSTATEY_KEY,
            "__VIEWSTATE": __VIEWSTATE,
            "__SCROLLPOSITIONX": __SCROLLPOSITIONX,
            "__SCROLLPOSITIONY": __SCROLLPOSITIONY,
            "__VIEWSTATEENCRYPTED": __VIEWSTATEENCRYPTED,
            "s$m$searchinputfield": "",
            "s$m$Content$Content$ListGridSelectionTree$folders:": "-70",
            "s$m$Content$Content$MarkChkDD": "-1",
            "s$m$Content$Content$SPSearchText$tb": "",
            "masterfootervalue": "X1!ÆØÅ",
            "LectioPostbackId": "",
        }
        message_session = Session.post(MESSAGE_URL, data=payload)
        message_soup = BeautifulSoup(message_session.text, features="html.parser")
        message_container = message_soup.find("div", {"class": "message-thread-container"})

        # Data extraction
        receivers = message_container.find("div", {"id": "s_m_Content_Content_MessageThreadCtrl_RecipientsReadMode"}).text.strip()
        message_thread_content = message_container.find("div", {"class": "message-thread-message-content"}).text.strip()
        sender = message_container.find("div", {"class": "message-thread-message-sender"}).find("span").text
        date = message_container.find("div", {"class": "message-thread-message-sender"}).text.split(',')[1].split(' ')[1]
        time = message_container.find("div", {"class": "message-thread-message-sender"}).text.split(',')[1].split(' ')[2].strip()
        topic = message_container.find("div", {"class": "message-thread-message-header"}).text.strip()

        # Add to dict
        messages_json[topic] = {
            "topic": topic,
            "sender": sender,
            "date": date,
            "time": time,
            "receivers": receivers,
            "message": message_thread_content,
        }
    if save_to_json:
        with open("messages.json", "w") as outfile:
            json.dump(messages_json, outfile, indent=4)
    return messages_json

    
        

        
        


    
    
