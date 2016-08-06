from aenum import Enum

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
        self.timeString = timeString.split("Please note")[0]
        if self.timeString.endswith(" - "): self.timeString = self.timeString.replace(" - ", "")
        self.timeObj = classTimes
        self.applyLink = ""

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

def filterSeminars(seminarList, fallTerm, springTerm, conflicts, searchTerms):
    conflictTimes = []
    searchTerms = searchTerms.split()
    for conflict in conflicts: conflictTimes.extend(timeStringToTimeBlockObjects(str(" and ".join(conflict.get("days")))  + ", " + str(conflict.get("starttime")) + "-" + str(conflict.get("endtime"))))

    seminars = [seminar for seminar in seminarList if ((((seminar.fallSem == True and fallTerm == True) or (seminar.fallSem == False and springTerm == True))) and (not any(seminarTime.conflicts(conflictTime) for conflictTime in conflictTimes for seminarTime in seminar.timeObj)))]
    if searchTerms: seminars = [x for x in seminars if any(keyword.lower() in str(x).lower() for keyword in searchTerms)]

    return seminars


def daysForString(str):
    days = str.replace(" & "," and ").split(" and ")
    daysToReturn = []
    for day in days:
        daysToReturn.append({"m": Day.Monday,"monday": Day.Monday,"mon": Day.Monday,"tues": Day.Tuesday,"t": Day.Tuesday,"tuesday": Day.Tuesday,"wednesday": Day.Wednesday,"w": Day.Wednesday,"wed": Day.Wednesday,"thursday": Day.Thursday,"th": Day.Thursday,"thurs": Day.Thursday,"friday": Day.Friday,"fri": Day.Friday,"f": Day.Friday}.get(day.lower(), Day.Unknown))
    return daysToReturn

def timeStringToTimeBlockObjects(str):
    if "[unavailable]" in str:
        return [TimeBlock(Day.Unknown, 0,0,0, 0)]

    timeStrings = str.split(",")
    days = daysForString(timeStrings[0].replace(",",""))
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
