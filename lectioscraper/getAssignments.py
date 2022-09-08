import json
from bs4 import BeautifulSoup
import logging


def filterAssignments(assignment_end_result, team, status, fravaer, karakter=""):
    filtered_assignments = {}
    for i in assignment_end_result:
        if (
            team != "alle hold"
            and status != "alle status"
            and fravaer != ""
            and karakter != ""
        ):
            if (
                i["hold"] == team
                and i["status"] == status
                and i["fravaer"] == fravaer
                and i["karakter"] == karakter
            ):
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status != "alle status"
            and fravaer != ""
            and karakter == ""
        ):
            if i["hold"] == team and i["status"] == status and i["fravaer"] == fravaer:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status != "alle status"
            and fravaer == ""
            and karakter != ""
        ):
            if (
                i["hold"] == team
                and i["status"] == status
                and i["karakter"] == karakter
            ):
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status != "alle status"
            and fravaer == ""
            and karakter == ""
        ):
            if i["hold"] == team and i["status"] == status:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status == "alle status"
            and fravaer != ""
            and karakter != ""
        ):
            if (
                i["hold"] == team
                and i["fravaer"] == fravaer
                and i["karakter"] == karakter
            ):
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status == "alle status"
            and fravaer != ""
            and karakter == ""
        ):
            if i["hold"] == team and i["fravaer"] == fravaer:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status == "alle status"
            and fravaer == ""
            and karakter != ""
        ):
            if i["hold"] == team and i["karakter"] == karakter:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team != "alle hold"
            and status == "alle status"
            and fravaer == ""
            and karakter == ""
        ):
            if i["hold"] == team:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status != "alle status"
            and fravaer != ""
            and karakter != ""
        ):
            if (
                i["status"] == status
                and i["fravaer"] == fravaer
                and i["karakter"] == karakter
            ):
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status != "alle status"
            and fravaer != ""
            and karakter == ""
        ):
            if i["status"] == status and i["fravaer"] == fravaer:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status != "alle status"
            and fravaer == ""
            and karakter != ""
        ):
            if i["status"] == status and i["karakter"] == karakter:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status != "alle status"
            and fravaer == ""
            and karakter == ""
        ):
            if i["status"] == status:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status == "alle status"
            and fravaer != ""
            and karakter != ""
        ):
            if i["fravaer"] == fravaer and i["karakter"] == karakter:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status == "alle status"
            and fravaer != ""
            and karakter == ""
        ):
            if i["fravaer"] == fravaer:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status == "alle status"
            and fravaer == ""
            and karakter != ""
        ):
            if i["karakter"] == karakter:
                filtered_assignments[i["opgavetitel"]] = i
        elif (
            team == "alle hold"
            and status == "alle status"
            and fravaer == ""
            and karakter == ""
        ):
            filtered_assignments[i["opgavetitel"]] = i
    return filtered_assignments


def get_assignments(
    to_json, team, status, fravaer, karakter, Session, SchoolId, studentId
):
    ASSIGNMENT_URL = (
        "https://www.lectio.dk/lectio/{}/OpgaverElev.aspx?elevid={}".format(
            SchoolId, studentId
        )
    )
    assignments = Session.get(ASSIGNMENT_URL)
    soup = BeautifulSoup(assignments.text, features="html.parser")
    assignment_table = soup.find(
        "table", {"class": "ls-table-layout1 maxW textTop lf-grid"}
    )
    assignment_rows = assignment_table.findAll("tr")[1:]
    assignment_end_result = []
    assignments = {}
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

    filtered = filterAssignments(assignment_end_result, team, status, fravaer, karakter)
    if len(filtered) == 0:
        return "Ingen opgaver fundet"
    if to_json:
        with open("assignments.json", "w") as file:
            json.dump(filtered, file, indent=4)

    return "Saved assignments to assignments.json" if to_json else filtered
