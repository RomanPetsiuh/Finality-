import os
import requests
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import apology


app = Flask(__name__)


app.config["TEMPLATES_AUTO_RELOAD"] = True



@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


db = SQL("sqlite:///programs.db")

x = []
x.append(0)


@app.route("/", methods=["GET", "POST"])
def homepage():


    if request.method == "POST":
        if not request.form.get("keyword"):
            return render_template("homepage.html")
        else:
            resultlist = db.execute("SELECT * FROM programlist WHERE title LIKE :key", key="%" + request.form.get("keyword") + "%")
            return render_template("results.html", results=resultlist)
    else:
        return render_template("homepage.html")


@app.route("/results", methods=["GET", "POST"])
def results():

    if request.method == "GET":
        if not request.form.get("title"):
            return render_template("results.html")
    else:
        programinfo = db.execute("SELECT * FROM programlist WHERE title = name",
                                 name=request.form.get("title"))
        return render_template("program.html", info=programinfo)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form["title"] or not request.form["org"] or not request.form["start"] or not request.form["end"] or not request.form["type"] or not request.form["website"] or not request.form["description"]:
            return apology("must provide information", 403)
        db.execute("INSERT INTO programlist (title, org, start, end, type, website, description) VALUES (:til, :org, :sta, :en, :typ, :web, :des)",
                   til=request.form["title"], org=request.form["org"], sta=request.form["start"], en=request.form["end"], typ=request.form["type"], web=request.form["website"], des=request.form["description"])
        p_id = db.execute("SELECT * FROM programlist WHERE title = :til", til=request.form["title"])
        p_id = p_id[0]
        p_id = str(p_id.get("id"))
        key = "/program?id=" + p_id
        return redirect(key)
    else:
        return render_template("register.html")

    return redirect("/")


@app.route("/program", methods=["GET", "POST"])
def program():
    """Display Program Information and Let User Write Review About the Program"""

    if request.method == "POST":
        if not request.form["nickname"] or not request.form["rating"] or not request.form["review"]:
            return apology("must provide information", 403)
        db.execute("INSERT INTO reviews (programid, nickname, rating, title, review) VALUES (:name, :nick, :rate, :til, :rev)",
                   name=x[0], nick=request.form["nickname"], rate=int(request.form["rating"]), til=request.form["title"], rev=request.form["review"])
        programrating = db.execute("SELECT AVG(rating) FROM reviews WHERE programid = :name", name=x[0])
        programrating = programrating[0]
        programrating = int(programrating.get("AVG(rating)"))
        db.execute("UPDATE programlist SET rating = :rate WHERE id = :name", rate=programrating, name=x[0])
        key = "/program?id=" + x[0]
        return redirect(key)

    else:
        p_id = request.args.get("id")
        x[0] = p_id
        programinfo = db.execute("SELECT * FROM programlist WHERE id = :name", name=p_id)
        userreviews = db.execute("SELECT * FROM reviews WHERE programid = :name", name=p_id)
        return render_template("program.html", info=programinfo[0], reviews=userreviews)

    return redirect("/")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
