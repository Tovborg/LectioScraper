
from lectioscraper.lectioscraper import Lectio
from lectioscraper.getSchedule import get_schedule
from lectioscraper.getAbsence import get_absence
from lectioscraper.getAllHomework import get_all_homework
from lectioscraper.getAssignments import get_assignments
from lectioscraper.getMessages import getMessages
from lectioscraper.lectioToCalendar import LecToCal

# export all function inside the Lectio class
__all__ = ['Lectio', 'get_schedule', 'get_absence', 'get_all_homework', 'get_assignments', 'getMessages', 'LecToCal']