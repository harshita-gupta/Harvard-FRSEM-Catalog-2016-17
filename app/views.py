from copy import deepcopy
from flask import render_template,  request
from .forms import FilterForm, ConflictForm 
from app import app
import pickle
from StringIO import StringIO
import pycurl
import re
from bs4 import BeautifulSoup
from aenum import Enum


alert = ""

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
    print str
    if "[unavailable]" in str:
        return [TimeBlock(Day.Unknown, 0,0,0, 0)]

    timeStrings = str.split(",")
    days = DaysForString(timeStrings[0].replace(",",""))
    timeblocks=[]
    for day in days:
        if day != Day.Unknown:
            times = timeStrings[1].strip().split(" ")[0].split("-")
            print times
            startTimes = times[0].split(":")
            endTimes = times[1].split(":")

            print startTimes
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

def filterSeminars(seminarList, fallTerm, springTerm, conflicts, searchTerms):
    conflictTimes = []
    for conflict in conflicts: 

        days = " and ".join(conflict.get("days"))
        new = timeStringToTimeBlockObjects(str(days)  + ", " + str(conflict.get("starttime")) + "-" + str(conflict.get("endtime")))

        conflictTimes.extend(new)

    seminars = [seminar for seminar in seminarList if ((((seminar.fallSem == True and fallTerm == True) or (seminar.fallSem == False and springTerm == True))) and (not any(seminarTime.conflicts(conflictTime) for conflictTime in conflictTimes for seminarTime in seminar.timeObj)))]
    print seminars

    searchTerms = searchTerms.split()
    # print searchTerms

    # if searchTerms:
    #     seminars = [x for x in seminars if any(keyword.lower() in repr(x).lower() for keyword in searchTerms)]
    # print seminars 
    # for seminar in seminars:

        
        # this has issues
        # Filtering based on search queries
        # if len(searchTerms) is not 0:
        #     searchQuery = searchTerms[0] in str(seminar)
        #     for searchTerm in searchTerms[1:]:
        #         searchQuery = searchQuery or searchTerm in repr(seminar)
        #     if searchQuery == False:
        #         seminars.remove(seminar)
        #         print "removed for keyword mismatch"
        #         print seminar.name
                

    return seminars
        # Filtering based on class timing
        # classTimes = seminar.timeObj
        # for classTime in classTimes:
        #     for conflictTime in conflictTimes:
        #         if conflictTime.conflicts(classTime) == True:
        #             displaySeminar[n] = False


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    # seminars = retrieveSeminars()
    # pickle.dump(seminars, open("seminars.pickle", "wb"))
    seminars = pickle.load(open("seminars.pickle", "rb"))
    form = request.form.copy()
    if request.method == 'POST':
        alert = ""
        print form
        searchKeywords = str(form['searchquery'])
        fallTerm = True if form.get('fallterm') else False
        springTerm = True if form.get('springterm') else False
        allConflictValues = {k: v for k,v in form.iteritems() if k.startswith("conflict")}
        conflicts = []
        numNextConflict = 1 
        moreConflicts = True
        while moreConflicts:
            if allConflictValues.get("conflict"+ str(numNextConflict) + "-day"):
                conflicts.append({"days": form.getlist("conflict"+ str(numNextConflict) + "-day"), "starttime" :  allConflictValues.get("conflict"+ str(numNextConflict) + "-starttime"), "endtime" : allConflictValues.get("conflict"+ str(numNextConflict) + "-endtime")})
                numNextConflict+= 1
            else:
                moreConflicts = False
        print conflicts
        seminarsToDisplay = filterSeminars(seminars, fallTerm, springTerm, conflicts, searchKeywords)

        return render_template('home.html', seminars= seminarsToDisplay, alert = alert)
    
    return render_template('home.html')
