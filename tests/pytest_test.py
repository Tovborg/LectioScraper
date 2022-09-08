from genericpath import isfile
import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # This is needed to import the module from the parent directory
from lectioscraper import *
client = Lectio("${{ secrets.LECTIO_USERNAME }}", "${{ secrets.LECTIO_PASSWORD }}", "${{ secrets.LECTIO_SCHOOL_ID }}")


def test_class_login_init():
    # Test if the class is initialized correctly
    assert client.Username == "emil763x"
    assert client.Password == "yApsCj@?8rQ&jMec"
    assert client.SchoolId == "59"
    # Test that the the the class is initialized correctly
    assert client.Username != "emil763x1"
    assert client.Password != "yApsCj@?8rQ&jMec1"
    assert client.SchoolId != "591"

    # check if self.studentid is not none
    assert client.studentId != None

def test_getSchedule():
    # Test that lectio has 'Session'
    assert hasattr(client, 'Session') == True
    # check that the function returns a dictionary
    assert type(client.getSchedule(to_json=False, print_to_console=False)) == dict
    assert client.getSchedule(to_json=True, print_to_console=False) == "saved in schedule.json"
    # in the current directory there should be a file called schedule.json and it should not be empty
    assert os.path.isfile("schedule.json") == True
    if os.path.isfile("schedule.json"):
        # remove the file
        os.remove("schedule.json")

def test_getTodaysSchedule():
    # Test that lectio has 'Session'
    assert hasattr(client, 'Session') == True
    # the function should either return a dictionary or a string
    assert type(client.getTodaysSchedule(to_json=False)) == dict or type(client.getTodaysSchedule(to_json=False)) == str
    assert client.getTodaysSchedule(to_json=True) == "Saved todays schedule to todaysSchedule.json" or client.getTodaysSchedule(to_json=True) == "No schedule found for today"
    if client.getTodaysSchedule(to_json=True) == "Saved todays schedule to todaysSchedule.json":
        # in the current directory there should be a file called todaysSchedule.json and it should not be empty
        assert os.path.isfile("todaysSchedule.json") == True
        if os.path.isfile("todaysSchedule.json"):
            # remove the file
            os.remove("todaysSchedule.json")

def test_getAllHomework():
    # Test that lectio has 'Session'
    assert hasattr(client, 'Session') == True
    # check that the function returns a dictionary
    assert type(client.getAllHomework(to_json=False, print_to_console=False)) == dict or type(client.getAllHomework(to_json=False, print_to_console=False)) == str
    assert client.getAllHomework(to_json=True, print_to_console=False) == "Saved homework to homework.json" or client.getAllHomework(to_json=True, print_to_console=False) == "No homework found"
    if client.getAllHomework(to_json=True, print_to_console=False) == "Saved homework to homework.json":
        # in the current directory there should be a file called homework.json and it should not be empty
        assert os.path.isfile("homework.json") == True
        if os.path.isfile("homework.json"):
            # remove the file
            os.remove("homework.json")

def test_getAssignments():
    # test that Lectio has 'Session'
    assert hasattr(client, 'Session') == True
    assert type(client.getAssignments(to_json=False)) == dict or type(client.getAssignments(to_json=False)) == str
    assert client.getAssignments(to_json=True) == "Saved assignments to assignments.json" or client.getAssignments(to_json=True) == "Ingen opgaver fundet"
    if client.getAssignments(to_json=True) == "Saved assignments to assignments.json":
        # in the current directory there should be a file called assignments.json and it should not be empty
        assert os.path.isfile("assignments.json") == True
        if os.path.isfile("assignments.json"):
            # remove the file
            os.remove("assignments.json")
    # test filter parameters
    karakterer = ["12", "10", "7", "4", "02", "00", "-3"]
    for karakter in karakterer:
        assert type(client.getAssignments(to_json=False, karakter=karakter)) == dict or type(client.getAssignments(to_json=False, karakter=karakter)) == str
        assert client.getAssignments(to_json=True, karakter=karakter) == "Saved assignments to assignments.json" or client.getAssignments(to_json=True, karakter=karakter) == "Ingen opgaver fundet"
        karakter_filtered = client.getAssignments(to_json=False, karakter=karakter)
        if karakter_filtered != "Ingen opgaver fundet":
            for assignment in karakter_filtered.keys():
                assert karakter_filtered[assignment]["karakter"] == karakter
                
def test_getAbsence():
    # test that Lectio has 'Session'
    assert hasattr(client, 'Session') == True
    assert type(client.getAbsence(to_json=False, written_assignments=False)) == dict or type(client.getAbsence(to_json=False)) == str
    assert client.getAbsence(to_json=True, written_assignments=False) == "Saved absence to absence.json" or client.getAbsence(to_json=True) == "No absence found"
    if client.getAbsence(to_json=True, written_assignments=False) == "Saved absence to absence.json":
        # in the current directory there should be a file called absence.json and it should not be empty
        assert os.path.isfile("absence.json") == True
        if os.path.isfile("absence.json"):
            # remove the file
            os.remove("absence.json")
    if client.getAbsence(to_json=False, written_assignments=True) != "No absence found":
        assert type(client.getAbsence(to_json=False, written_assignments=True)) == dict
        written_assignment = client.getAbsence(to_json=False, written_assignments=True)
        for i in written_assignment.keys():
            assert 'writing' in written_assignment[i].keys()
            assert type(written_assignment[i]["writing"]) == dict
    if client.getAbsence(to_json=False, written_assignments=False) != "No absence found":
        assert type(client.getAbsence(to_json=False, written_assignments=False)) == dict
        written_assignment = client.getAbsence(to_json=False, written_assignments=False)
        for i in written_assignment.keys():
            # make sure there is not a key called 'writing'
            assert 'writing' not in written_assignment[i].keys()
    
def test_getAllUnreadMessages():
    # test that Lectio has 'Session'
    assert hasattr(client, 'Session') == True
    assert type(client.getUnreadMessages(to_json=False, get_content=True)) == dict or type(client.getUnreadMessages(to_json=False, get_content=True)) == str
    assert client.getUnreadMessages(to_json=True, get_content=True) == "Saved unread messages to unread_messages.json" or client.getUnreadMessages(to_json=True, get_content=True) == "No unread messages"
    if client.getUnreadMessages(to_json=True, get_content=True) == "Saved unread messages to unread_messages.json":
        # in the current directory there should be a file called unread_messages.json and it should not be empty
        assert os.path.isfile("unread_messages.json") == True
        with open("unread_messages.json", "r") as f:
            assert len(f.read()) != 0
        if os.path.isfile("unread_messages.json"):
            # remove the file
            os.remove("unread_messages.json")
    if client.getUnreadMessages(to_json=False, get_content=True) != "No unread messages":
        assert type(client.getUnreadMessages(to_json=False, get_content=True)) == dict
        unread_messages = client.getUnreadMessages(to_json=False, get_content=True)
        for i in unread_messages.keys():
            assert 'content' in unread_messages[i].keys()
            assert type(unread_messages[i]["content"]) == str
    if client.getUnreadMessages(to_json=False, get_content=False) != "No unread messages":
        assert type(client.getUnreadMessages(to_json=False, get_content=False)) == dict
        unread_messages = client.getUnreadMessages(to_json=False, get_content=False)
        for i in unread_messages.keys():
            # make sure there is not a key called 'content'
            assert 'content' not in unread_messages[i].keys()
                
    
    
            
        
                
    
    

    