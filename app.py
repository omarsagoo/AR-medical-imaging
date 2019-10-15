import os

from flask import Flask, redirect, render_template, request, url_for
from pymongo import MongoClient

client = MongoClient()
db = client.get_default_database()
medfiles = db.medfiles

app = Flask(__name__)



