# The MIT License (MIT)
# Copyright (c) 2016 Harshita Gupta
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from model import Seminar
import pickle
from StringIO import StringIO
import pycurl
import re
from bs4 import BeautifulSoup
from model import timeStringToTimeBlockObjects

baseurl = "http://freshsem.fas.harvard.edu/public/"
url = "http://freshsem.fas.harvard.edu/public/sem-list.cgi?query=&searchdesc=1&sort=#1/"
studentApplyPortal = "http://www.freshsem.fas.harvard.edu/student/"

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
    website = seminarhtml.a['href'] if not seminarhtml.a['href']=="sem-list.cgi#1" else None
    description = seminarhtml.h2.next_sibling.next_sibling.text

    seminarobj = Seminar(name, instructor, courseNum, catNum, sem, cap, classTimes, timeString, location, description, website)
    return seminarobj

def retrieveSeminars():
    print "Generating list of seminars..."

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
        seminarlinks.append((baseurl + row['href'], studentApplyPortal + row['href']))

    seminars = []

    print "Downloading seminar information..."

    for seminarlink in seminarlinks:
        seminarobj = linkToSeminarObj(seminarlink[0])
        seminarobj.applyLink =  seminarlink[1]
        seminars.append(seminarobj)
        print "Downloaded " + seminarobj.name

    print "All seminars downloaded!"

    return seminars