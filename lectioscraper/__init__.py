
from lectioscraper.lectioscraper import Lectio
from lectioscraper.getSchedule import get_schedule
from lectioscraper.getAbsence import get_absence
from lectioscraper.getAllHomework import get_all_homework
from lectioscraper.getAssignments import get_assignments
from lectioscraper.getTodaysSchedule import get_todays_schedule
from lectioscraper.getUnreadMessages import get_unread_messages

# export all function inside the Lectio class
__all__ = ['Lectio', 'get_schedule', 'get_absence', 'get_all_homework', 'get_assignments', 'get_todays_schedule', 'get_unread_messages']