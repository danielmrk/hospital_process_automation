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

data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A1" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A2" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A3" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A4" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B1" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B2" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B3" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B4" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "ER" + "\", \"arrivalTime\":\"" + str(500) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)