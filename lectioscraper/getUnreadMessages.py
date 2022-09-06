from bs4 import BeautifulSoup
import json
import requests

def get_unread_messages(to_json, SchoolId, studentId, Session, get_content):
    soup = BeautifulSoup(Session.get("https://www.lectio.dk/lectio/{}/beskeder2.aspx?type=&elevid={}&selectedfolderid=-70".format(SchoolId, studentId)).text, "html.parser")
    unread_messages = soup.find_all("tr", {"class": "unread"})
    if len(unread_messages) == 0:
        return "No unread messages"
    unr_messages = {}
    for i in unread_messages:
        td = i.find_all("td")
        # create a list comprehension called useful data, which loops through the td list and checks if its empty or not and if it is not empty, strip it from \n and append it to the list
        useful_data = [x.text.strip("\n") for x in td if x.text.strip("\n") != ""]
        
        if get_content is False:
            unr_messages[useful_data[0]] = {
                "title": useful_data[0],
                "latest_message_sender": useful_data[1],
                "first_message_sender": useful_data[2],
                "to": useful_data[3],
                "day_and_data": useful_data[4],
                "date": useful_data[4][3::],
            }
        else:
            # get postback id from the link
            postback_id = i.find("div", {"class": "buttonlink"}).find("a")["onclick"].split("'")[3].split("_")[3]
            url = "https://www.lectio.dk/lectio/{}/beskeder2.aspx?type=showthread&elevid={}&selectedfolderid=-70&id={}".format(SchoolId, studentId, postback_id)
            content = Session.get(url)
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
            
            # the above code is replacing the danish characters with english characters, because the danish characters are not supported by the json module please make it cleaner
            danish_chars_to_english = (
                ("æ", "ae"),
                ("ø", "oe"),
                ("å", "aa"),
                ("Æ", "Ae"),
                ("Ø", "Oe"),
                ("Å", "Aa"),
            )
            
            for char in danish_chars_to_english:
                message = message.replace(char[0], char[1])
                emne = emne.replace(char[0], char[1])
                afsender = afsender.replace(char[0], char[1])
                til = til.replace(char[0], char[1])
                message = message.replace(char[0], char[1])
                useful_data[0] = useful_data[0].replace(char[0], char[1])
                useful_data[1] = useful_data[1].replace(char[0], char[1])
                useful_data[2] = useful_data[2].replace(char[0], char[1])
                useful_data[3] = useful_data[3].replace(char[0], char[1])
                useful_data[4] = useful_data[4].replace(char[0], char[1])


            unr_messages[useful_data[0]] = {
                "title": emne,
                "latest_message_sender": useful_data[1],
                "sender": afsender,
                "to": til,
                "content": message,
                "day_and_date": useful_data[4],
                "date": useful_data[4][3::]
            }
    if to_json:
        with open("unread_messages.json", "w") as f:
            json.dump(unr_messages, f, indent=4)
    return unr_messages if to_json is False else "Saved to unread_messages.json"
        