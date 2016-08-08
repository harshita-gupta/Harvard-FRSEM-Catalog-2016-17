# The MIT License (MIT)
# Copyright (c) 2016 Harshita Gupta
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from flask import render_template, request
from app import app
import pickle
import socket
import keen
from model import filterSeminars, Seminar, TimeBlock, Day
from datasource import retrieveSeminars

keen.project_id = "57a4ec410727190b418cc7fc"
keen.write_key = "3e8d74ce621627a69bb65ba5a0e7eb4877fe51c1ea62703708a3c28e5bbaaf53c28f0b97d7f3baddf19d98e9a08b634c88fbc13c9c3b39a46873f2f0154dd4e461488c13bce00d4cb2c913a2586c3fff6151d3540b74d6b3518cc3eba8b7cbcf"

alert = ""
applyLinks = ""


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():

    # seminars = retrieveSeminars()
    # pickle.dump(seminars, open("seminars.pickle", "wb"))
    seminars = pickle.load(open("seminars.pickle", "rb"))
    form = request.form.copy()

    if request.method == 'POST':
        alert = ""
        searchKeywords = str(form['searchquery'])
        fallTerm = True if form.get('fallterm') else False
        springTerm = True if form.get('springterm') else False
        allConflictValues = {k: v for k, v in form.iteritems()
                             if k.startswith("conflict")}
        conflicts = []
        numNextConflict = 1
        moreConflicts = True
        while moreConflicts:
            if allConflictValues.get("conflict" +
                                     str(numNextConflict) + "-day"):
                conflicts.append(
                    {"days": form.getlist(
                        "conflict" + str(numNextConflict) + "-day"),
                     "starttime": allConflictValues.get(
                        "conflict" + str(numNextConflict) + "-starttime"),
                     "endtime": allConflictValues.get(
                        "conflict" + str(numNextConflict) + "-endtime")})
                numNextConflict += 1
            else:
                moreConflicts = False
        keen.add_event("seminar_loads",
        {"fallterm" : str(fallTerm),
        "springterm" : str(springTerm),
        "searches": str(searchKeywords),
        "conflicts": str(conflicts) })
        seminarsToDisplay = filterSeminars(
            seminars, fallTerm, springTerm, conflicts, searchKeywords)

        return render_template(
            'index.html', seminars=seminarsToDisplay, alert=alert)

    keen.add_event("homepage_loads", {"ip":request.remote_addr})
    return render_template('index.html')
