# -*- coding: utf-8 -*-

from configparser import ConfigParser
import sqlite3
from flask import abort, Flask, render_template, redirect, request, session
from flask_httpauth import HTTPDigestAuth
import tweepy

import articles
import auth

CONFIG = ConfigParser()
CONFIG.read("config/feelest.ini", encoding="utf-8")

APP = Flask("feelest")

DBCONN = sqlite3.connect("database/" + CONFIG["system"]["dbname"])
DBCONN.row_factory = sqlite3.Row
DB = DBCONN.cursor()

debug = True if CONFIG["system"]["debug"] == "True" else False

@APP.route("/")
def index():
    """
    Return index page
    """
    article_list = articles.get_articles(
        db=DB, invisible=True, timeformat=CONFIG["system"]["time_format"], url=CONFIG["blog"]["url"]
    )
    return render_template("index.tmpl", blog=CONFIG["blog"], articles=article_list)

@APP.route("/article/<string:articleid>")
def article(articleid):
    """
    Return article page
    """
    if articles.exist_article(db=DB, articleid=articleid, invisible=True) and articleid.isdigit():
        article_data = dict(
            articles.get_article(db=DB, articleid=articleid, invisible=True, timeformat=CONFIG["system"]["time_format"], url=CONFIG["blog"]["url"])
        )
        return render_template("article.tmpl", blog=CONFIG["blog"], article=article_data, is_article=True)
    abort(404)

@APP.route("/login", methods=["GET", "POST"])
def login():
    """
    Login with digest or oauth
    """
    if request.method == "POST":
        if CONFIG["system"]["authenticator"] == "digest":
            session["username"] = request.form["username"]
            return redirect(request.referrer or "/")
    return render_template("login.tmpl")

@APP.route("/logout")
def logout():
    """
    Logout from feelest
    """
    session.pop("session_token", None)
    return redirect(request.referrer or "/")

if __name__ == "__main__":
    APP.run(host="0.0.0.0")
