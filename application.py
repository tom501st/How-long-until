from flask import Flask, render_template, request, session, redirect, g, url_for, flash
import os, re
from cs50 import SQL
import time
import datetime
from datetime import datetime as datetime1
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = os.urandom(18)

db = SQL("sqlite:///dates.db")

@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']

def formatDate(dateinput):
    # input must be in exact format of 'YYYY-MM-DD HH:MM'
    day = dateinput[8:10]
    month = dateinput[5:7]
    year = dateinput[0:4]
    time = dateinput[11:16]

    month_number = month
    datetime_object = datetime.datetime.strptime(month_number, "%m")
    month_name = datetime_object.strftime("%b")

    dateformatted = month_name + ' ' + day + ' ' + year + ' ' + time

    return dateformatted


@app.route('/', methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if request.form.get("submit_a"):
            dispname = request.form["date"]

            datetable = db.execute("SELECT date FROM dates WHERE dispname=:dispname", dispname=dispname)
            for row in datetable:
                date = row["date"]

            return render_template("countdown.html", dispname=dispname, dateformatted=formatDate(date)) #untilOrSince='Until'


        if request.form.get("submit_b"):
            randrows = db.execute("SELECT * FROM dates WHERE date > DATETIME('now') ORDER BY random() LIMIT 4")
            return render_template("index.html", rows=randrows)

        if request.form.get("submit_c"):

            dateinput = request.form["date_input"]

            if dateinput == "":
                return "Error: no custom date was inputted"

            if len(dateinput) > 16:
        	    return "Error: please ensure your date-time doesn't have a space at the end or any other character."


            if len(dateinput) != 16 or dateinput[4] != '-' or dateinput[7] != '-' or dateinput[10] != ' ' or dateinput[13] != ':':
        	    return "Error: please ensure your date-time follows the correct format. (e.g. 2025-03-21 14:30)"

            iList = [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15]
            for i in iList:
                if (dateinput[i].isnumeric() == False):
                    return "Error: please check your input for misplaced characters and format correctly. (e.g. 2025-03-21 14:30)"

            # if datetime1.strptime(dateinput, '%Y-%m-%d %H:%M') > datetime1.now():
                # return render_template("countdown.html", untilOrSince='Until', dispname=dateinput, dateformatted=formatDate(dateinput))

            # elif datetime1.strptime(dateinput, '%Y-%m-%d %H:%M') < datetime1.now():
                # return render_template("countdown.html", untilOrSince='Since', dispname=dateinput, dateformatted=formatDate(dateinput))

            return render_template("countdown.html", dispname=dateinput, dateformatted=formatDate(dateinput))

    else:
        rows = db.execute("SELECT * FROM dates WHERE date > DATETIME('now') LIMIT 4")

        return render_template("index.html", rows=rows)



@app.route('/how-long-since', methods=["POST", "GET"])
def howLongSince():
    if request.method == "POST":

        if request.form.get("submit_a"):
            dispname = request.form["date"]

            datetable = db.execute("SELECT date FROM dates WHERE dispname=:dispname", dispname=dispname)
            for row in datetable:
                date = row["date"]

            return render_template("countdown.html", dispname=dispname, dateformatted=formatDate(date)) #untilOrSince='Since',


        if request.form.get("submit_b"):
            randrows = db.execute("SELECT * FROM dates WHERE date < DATETIME('now') AND canExpire = 'no' ORDER BY random() LIMIT 4;")
            return render_template("howlongsince.html", rows=randrows)

    else:
        rows = db.execute("SELECT * FROM dates WHERE date < DATETIME('now') AND canExpire = 'no' LIMIT 4;")

        return render_template("howlongsince.html", rows=rows)


@app.route("/custom-dates", methods=["GET", "POST"])
def custom_dates():
    if request.method == "POST":

        if request.form.get("submit_a"):
            dispname = request.form["date"]

            datetable = db.execute("SELECT date FROM customDates WHERE dispname=:dispname", dispname=dispname)
            for row in datetable:
                date = row["date"]

            # if datetime1.strptime(date, '%Y-%m-%d %H:%M') > datetime1.now():
                # return render_template("countdown.html", untilOrSince='Until', dispname=dispname, dateformatted=formatDate(date))

            # elif datetime1.strptime(date, '%Y-%m-%d %H:%M') < datetime1.now():
                # return render_template("countdown.html", untilOrSince='Since', dispname=dispname, dateformatted=formatDate(date))

            return render_template("countdown.html", dispname=dispname, dateformatted=formatDate(date))

        if request.form.get("submit_b"):
            randrows = db.execute("SELECT * FROM customDates WHERE belongsTo=:user ORDER BY random() LIMIT 5", user=session['user'].lower())
            return render_template("customdates.html", rows=randrows, user=session['user'])

        if request.form.get("delete"):
            db.execute("DELETE FROM customDates WHERE dispname=:dispname AND belongsTo = :user", dispname=request.form["date"] , user=session['user'])

            flash("Custom date successfully deleted", "flashes")
            return redirect("/custom-dates")



        if request.form.get("customSubmit"):

            nameinput = request.form["eventName_input"]
            dateinput = request.form["date_input"]

            if dateinput == "":
                return "Error: no custom date was inputted"

            if len(dateinput) > 16:
        	    return "Error: please ensure your date-time doesn't have a space at the end or any other character."


            if len(dateinput) != 16 or dateinput[4] != '-' or dateinput[7] != '-' or dateinput[10] != ' ' or dateinput[13] != ':':
        	    return "Error: please ensure your date-time follows the correct format. (e.g. 2025-03-21 14:30)"

            iList = [0, 1, 2, 3, 5, 6, 8, 9, 11, 12, 14, 15]
            for i in iList:
                if (dateinput[i].isnumeric() == False):
                    return "Error: please check your input for misplaced characters and format correctly. (e.g. 2025-03-21 14:30)"

            # check if custom date name is unique / already exists
            rows = db.execute("SELECT * FROM customDates WHERE uniquename=:nameinput", nameinput=nameinput)
            if len(rows) != 0:
                flash("You have already created a custom date with that name.", "flashes")
                return redirect("/custom-dates")

            if request.form["canExpire"] == 'yes':
                canExpire = 'yes'
            else:
                canExpire = 'no'

            # save custom date in database
            db.execute("INSERT INTO customDates(dispname, uniquename, date, canExpire, belongsTo) VALUES(:dispname, :uniquename, :date, :canExpire, :belongsTo)"
            , dispname=nameinput, uniquename=nameinput, date=dateinput, canExpire=canExpire, belongsTo=session['user'].lower())

            flash("Your new custom date has been saved successfully", "flashes-green")
            return redirect("/custom-dates")
    else:
        # if logged in
        if g.user:
            # clears all expired dates for all users in database
            db.execute("DELETE FROM customDates WHERE canExpire='yes' AND date < :currentDT", currentDT=datetime1.now())

            rows = db.execute("SELECT * FROM customDates WHERE belongsTo=:user LIMIT 5", user=session['user'].lower())
            return render_template("customdates.html", user=session['user'], rows=rows)


        # if user is not logged in
        else:
            flash("You must log into an account to create custom dates", "flashes")
            return redirect("/login")


@app.route("/logout")
def logout():
    # if logged in
    g.user = None
    session.clear()
    session.pop('user', None)
    session['logged_in'] = False

    if g.user:
        flash('logout failed', 'flashes-red')
    else:
        flash('You have been logged out', 'flashes')

    return redirect("/")



@app.route("/login", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        # log user in
        session.pop('user', None)
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form['username'].lower())


        if len(rows) != 1:
            flash('Username not found', 'flashes-red')
            return render_template("login.html")

        if not check_password_hash(rows[0]["hash"], request.form['psw']):
            flash('Incorrect password', 'flashes-red')
            return render_template("login.html")
        else:
            session['user'] = request.form['username']
            session['logged_in'] = True
            flash('Login successful', 'flashes-green')
            return redirect("/custom-dates")
    else:
        if g.user:
            flash('You are already logged in', 'flashes')
            return redirect("/")
        else:
            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        psw = request.form.get("psw")
        confPassword = request.form.get("confpassword")

        if username == '' or psw == '' or confPassword == '':
            return 'Error: fields cannot be left empty'
        if psw != confPassword:
            return 'Error: passwords do not match'
        if len(psw) < 8:
            return 'Error: password must be at least 8 characters long'
        elif re.search('[0-9]',psw) is None:
            return 'Error: password must contain a digit'
        elif re.search('[A-Z]',psw) is None:
            return 'Error: password must contain a capital letter'
        elif re.search('[a-z]',psw) is None:
            return 'Error: password must contain a lowercase letter'
        elif len(db.execute("SELECT username FROM users WHERE username=:username", username=username.lower())) != 0:
            return 'Error: username already exists'

        else:
            # add user details to database
            hashpw = generate_password_hash(psw, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashpw)", username=username.lower(), hashpw=hashpw)

            session['user'] = request.form['username']
            session['logged_in'] = True

            flash('You are now logged in', 'flashes-green')
            return redirect("/")

    else:
        return render_template("register.html")

# my custom dates (display dates, add new dates)

# my account (log in/register, log out)


