# The MIT License (MIT)
# Copyright (c) 2016 Harshita Gupta
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from aenum import Enum


class TimeBlock:
    def __init__(self, day, startH, startM, endH, endM):
        self.day = day
        self.startTime = startH + (startM / 60)
        if self.startTime < 9 and self.startTime != 0:
            self.startTime = self.startTime + 12

        self.endTime = endH + (endM / 60)
        if self.endTime < 11.1 and self.endTime != 0:
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
    def __init__(self,
                 name, instructor, courseNum, catalogNum, sem, cap,
                 classTimes, timeString, loc, description, website):
        self.name = name
        self.instructor = instructor
        self.courseNum = courseNum
        self.catalogNum = catalogNum
        self.capacity = cap
        self.location = loc
        if sem == "Offered Fall Semester":
            self.fallSem = True
        else:
            self.fallSem = False
        self.description = description
        self.website = website
        self.timeString = timeString.split("Please note")[0]
        if self.timeString.endswith(" - "):
            self.timeString = self.timeString.replace(" - ", "")
        self.timeObj = classTimes
        self.applyLink = ""

    def __str__(self):
        esc = "\n"
        str = repr(self.name) + esc
        str += "Instructor: " + repr(self.instructor) + esc
        str += "Course Number: " + repr(self.courseNum) + esc
        if self.fallSem:
            str += "Fall 2016" + esc
        else:
            str += "Spring 2017" + esc
        str += "Catalog Number: " + repr(self.catalogNum) + esc
        str += "Capacity: " + repr(self.capacity) + " students" + esc
        str += repr(self.location) + esc
        str += repr(self.timeString) + esc
        str += repr(self.description) + esc
        str += "Course website: " + repr(self.website)
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
    for conflict in conflicts:
        conflictTimes.extend(
            timeStringToTimeBlockObjects(
                str(" and ".join(conflict.get("days"))) +
                ", " +
                str(conflict.get("starttime")) +
                "-" +
                str(conflict.get("endtime"))))

    seminars = [seminar for seminar in seminarList if
                ((((seminar.fallSem is True and fallTerm is True) or
                    (seminar.fallSem is False and springTerm is True))) and
                    (not any(seminarTime.conflicts(conflictTime)
                             for conflictTime in conflictTimes
                             for seminarTime in seminar.timeObj)))]
    if searchTerms:
        seminars = [x for x in seminars if
                    any(keyword.lower() in str(x).lower()
                        for keyword in searchTerms)]

    return seminars


def daysForString(str):
    days = str.replace(" & ", " and ").split(" and ")
    daysToReturn = []
    for day in days:
        daysToReturn.append(
            {"m": Day.Monday, "monday": Day.Monday, "mon": Day.Monday,
             "tues": Day.Tuesday, "t": Day.Tuesday, "tuesday": Day.Tuesday,
             "wednesday": Day.Wednesday, "w": Day.Wednesday,
             "wed": Day.Wednesday,
             "thursday": Day.Thursday, "th": Day.Thursday,
             "thurs": Day.Thursday,
             "friday": Day.Friday, "fri": Day.Friday, "f": Day.Friday}.
            get(day.lower(), Day.Unknown))
    return daysToReturn


def timeStringToTimeBlockObjects(str):
    if "[unavailable]" in str:
        return [TimeBlock(Day.Unknown, 0, 0, 0, 0)]

    timeStrings = str.split(",")
    days = daysForString(timeStrings[0].replace(",", ""))
    timeblocks = []
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

            endH = float(endTimes[0].replace("pm", "").
                         replace("am", "").replace("N", ""))
            if len(endTimes) > 1:
                endM = float(endTimes[1])
            else:
                endM = float(0)
        else:
            startM = startH = endM = endH = float(0)

        timeblocks.append(TimeBlock(day, startH, startM, endH, endM))
    return timeblocks
