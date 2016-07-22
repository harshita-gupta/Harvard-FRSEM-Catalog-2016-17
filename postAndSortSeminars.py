__author__ = 'Harshita'


from datetime import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO
import pycurl
import re
import time
import pandas as pd
from aenum import Enum



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
        daysToReturn.append({"Monday": Day.Monday,"Tuesday": Day.Tuesday,"Wednesday": Day.Wednesday,"Thursday": Day.Thursday,"Friday": Day.Friday,}.get(day, Day.Unknown))
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
    description = seminarhtml.h2.next_sibling.next_sibling

    seminarobj = Seminar(name, instructor, courseNum, catNum, sem, cap, classTimes, timeString, location, description, website)
    return seminarobj

for seminarlink in seminarlinks:
    seminars.append(linkToSeminarObj(seminarlink))



