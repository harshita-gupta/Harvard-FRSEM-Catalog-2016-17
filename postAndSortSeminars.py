__author__ = 'Harshita'

import pickle
from bs4 import BeautifulSoup
from StringIO import StringIO
import pycurl
import re
from aenum import Enum

class Seminar:
    def __init__(self, name, instructor, courseNum, catalogNum, sem, cap, classTimes, timeString, loc, description, website):
        self.name = name
        self.instructor = instructor
        self.courseNum = courseNum
        self.catalogNum = catalogNum
        self.capacity = cap
        self.location = loc
        if sem == "Offered Fall Semester":
            self.fallSem = True;
        else:
            self.fallSem = False;
        self.description = description
        self.website = website
        self.timeString = timeString
        self.timeObj = classTimes

    def __str__(self):
        esc = "\n"
        str = repr(self.name) + esc +"Instructor: " + repr(self.instructor) + esc + "Course Number: " + repr(self.courseNum) + esc
        if self.fallSem:
            str += "Fall 2016" + esc
        else:
            str += "Spring 2017" + esc
        str += "Catalog Number: " + repr(self.catalogNum) + esc
        str += "Capacity: " + repr(self.capacity) + " students" + esc
        str += repr(self.location) + esc
        str += repr(self.timeString) + esc
        str += repr(self.description) + esc
        str += "Course website: " +repr(self.website)
        return str

class Day(Enum):
    Unknown = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5

def DaysForString(str):

    days = str.replace(" & "," and ").split(" and ")
    daysToReturn = []
    for day in days:
        daysToReturn.append({"m": Day.Monday,"monday": Day.Monday,"mon": Day.Monday,"tues": Day.Tuesday,"t": Day.Tuesday,"tuesday": Day.Tuesday,"wednesday": Day.Wednesday,"w": Day.Wednesday,"wed": Day.Wednesday,"thursday": Day.Thursday,"th": Day.Thursday,"thurs": Day.Thursday,"friday": Day.Friday,"fri": Day.Friday,"f": Day.Friday}.get(day.lower(), Day.Unknown))
    return daysToReturn

class TimeBlock:
    def __init__(self, day, startH, startM, endH, endM):
        self.day = day
        self.startTime = startH + (startM/60)
        if self.startTime<9 and self.startTime!= 0:
            self.startTime = self.startTime + 12

        self.endTime = endH + (endM/60)
        if self.endTime<11.1 and self.endTime!= 0:
            self.endTime = self.endTime + 12

    def conflicts(self, withTimeBlock):
        if withTimeBlock.day != self.day:
            return False
        if withTimeBlock.startTime >= self.endTime:
            return False
        if withTimeBlock.endTime <= self.startTime:
            return False
        return True

def timeStringToTimeBlockObjects(str):
    if "[unavailable]" in str:
        return [TimeBlock(Day.Unknown, 0,0,0, 0)]

    timeStrings = str.split(",")
    days = DaysForString(timeStrings[0].replace(",",""))
    timeblocks=[]
    for day in days:
        if day != Day.Unknown:
            times = timeStrings[1].strip().split(" ")[0].split("-")
            startTimes = times[0].split(":")
            endTimes = times[1].split(":")

            startH = float(startTimes[0])
            if len(startTimes) > 1:
                startM = float(startTimes[1])
            else:
                startM = float(0)

            endH = float(endTimes[0].replace("pm", "").replace("am", "").replace("N", ""))
            if len(endTimes) > 1:
                endM = float(endTimes[1])
            else:
                endM = float(0)
        else:
            startM = startH = endM = endH = float(0)

        timeblocks.append(TimeBlock(day, startH, startM, endH, endM))
    return timeblocks

def linkToSeminarObj(link):
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, link)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()
    seminarhtml = BeautifulSoup(content)


    name = seminarhtml.h1.text
    instructor = seminarhtml.p.em.text
    courseNumElem = seminarhtml.p.next_sibling.next_sibling.b
    courseNum = courseNumElem.text
    catNumElem = courseNumElem.next_sibling.next_sibling.next_sibling
    catNum = catNumElem.text.strip()
    sem = catNumElem.next_sibling.next_sibling.strip()
    capElem =  catNumElem.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling
    cap = int(capElem.text.strip())
    meetingTimeElem = capElem.next_sibling.next_sibling.next_sibling.next_sibling
    meetingTimeString = meetingTimeElem.text
    timeString = meetingTimeString
    classTimes =  timeStringToTimeBlockObjects(meetingTimeString)

    location =meetingTimeElem.next_sibling.next_sibling.next_sibling.text
    website = seminarhtml.a['href']
    description = seminarhtml.h2.next_sibling.next_sibling.text

    seminarobj = Seminar(name, instructor, courseNum, catNum, sem, cap, classTimes, timeString, location, description, website)
    return seminarobj

def retrieveSeminars():
    print "Generating list of seminars..."
    baseurl = "http://freshsem.fas.harvard.edu/public/"
    url = "http://freshsem.fas.harvard.edu/public/sem-list.cgi?query=&searchdesc=1&sort=#1/"
    storage = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, storage.write)
    c.perform()
    c.close()
    content = storage.getvalue()
    htmldoc = BeautifulSoup(content)

    rows = htmldoc.find_all(href=re.compile('seminar'))
    seminarlinks = []
    for row in rows:
        seminarlinks.append(baseurl + row['href'])

    seminars = []

    print "Downloading seminar information..."

    for seminarlink in seminarlinks:
        seminarobj = linkToSeminarObj(seminarlink)
        seminars.append(seminarobj)
        print "Downloaded " + seminarobj.name

    print "All seminars downloaded!"

    return seminars

def ynToTrueFalse(prompt):
    input = raw_input(prompt)
    if (input.lower().strip() == "y" or input.lower().strip() == "yes"):
        return True
    else:
        return False


# seminars = retrieveSeminars()
# pickle.dump(seminars, open("seminars.pickle", "wb"))

seminars = pickle.load(open("seminars.pickle", "rb"))

displaySeminar = [True] * len(seminars)

print "Set up your filters for what seminars you want listed."

term = raw_input("Do you want to see seminars from Fall term, Spring term, or both? Respond with F, S, or B.")
term = term.strip().lower()

print "Enter dates and times of all conflicting committments/ classes during which you can't take a seminar."
print "Example: I plan to take CS61, which is T Th 2:30-4, so I cannot have a seminar then."

conflictTimes = []
classdatesToEnter = ynToTrueFalse('Would you like to enter a conflict? Respond with Y or N.')

while (classdatesToEnter == True or classdatesToEnter == "True"):
    dayOfWeek = raw_input('Enter the day of your other committment, as M or m or Monday. Separate multiple days with \" and \".')
    timeSlot = raw_input('Enter the time of the other committment, using 24 hour clock. Do not include PM or AM. '
                     'Separate start and end time with a simple dash (-). Eg. \'13-15:30\'')
    conflictTimes.extend(timeStringToTimeBlockObjects(dayOfWeek + ", " + timeSlot))
    classdatesToEnter = ynToTrueFalse('Would you like to enter another conflict? Respond with Y or N.')

searchTerms = raw_input("Enter keywords to search for, separated by spaces.")
searchTerms = searchTerms.split()

for n in range(0, len(seminars) - 1):
    seminar = seminars[n]

    # Filtering based on term
    if ((seminar.fallSem == True and term == "s") or (seminar.fallSem == False and term == "f")):
        displaySeminar[n] = False

    # Filtering based on search queries
    if len(searchTerms) is not 0:
        searchQuery = searchTerms[0] in str(seminar)
        for searchTerm in searchTerms[1:]:
            searchQuery = searchQuery or searchTerm in repr(seminar)
        if searchQuery == False:
            displaySeminar[n] = False
            continue

    # Filtering based on class timing
    classTimes = seminar.timeObj
    for classTime in classTimes:
        for conflictTime in conflictTimes:
            if conflictTime.conflicts(classTime) == True:
                displaySeminar[n] = False


for n in range(0, len(seminars) - 1):
    if displaySeminar[n] == True:
        print str(seminars[n]) + "\n"