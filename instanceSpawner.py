#! /usr/bin/python3
from bottle import  route, run, template, request, response
import sqlite3
import requests
import numpy
import json
from datetime import datetime
import queue
import time
import random


counter = 500
for i in range(30):

    counter += 60
    
    randomNumber = random.random()
    patientType = "A1"

    if randomNumber < (1/9):
        patientType = "A1"
    elif randomNumber < (2/9):
        patientType = "A2"
    elif randomNumber < (3/9):
        patientType = "A3"
    elif randomNumber < (4/9):
        patientType = "A4"
    elif randomNumber < (5/9):
        patientType = "B1"
    elif randomNumber < (6/9):
        patientType = "B2"
    elif randomNumber < (7/9):
        patientType = "B3"
    elif randomNumber < (8/9):
        patientType = "B4"
    elif randomNumber < (9/9):
        patientType = "ER"

    data = {
                "behavior": "fork_running",
                "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
                "init": "{\"patientType\":\"" + patientType + "\", \"arrivalTime\":\"" + str(counter) + "\"}"
                }
            
    response = requests.post("https://cpee.org/flow/start/url/", data = data)
    time.sleep(1)
