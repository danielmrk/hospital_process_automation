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
            "init": "{\"patientType\":\"" + "A1" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A2" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A3" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A4" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B1" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B2" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B3" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B4" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "ER" + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)