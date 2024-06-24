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
            "init": "{\"patientType\":\"" + "A2" + "\", \"arrivalTime\":\"" + str(600) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A3" + "\", \"arrivalTime\":\"" + str(620) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A4" + "\", \"arrivalTime\":\"" + str(630) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B1" + "\", \"arrivalTime\":\"" + str(640) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B2" + "\", \"arrivalTime\":\"" + str(645) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B3" + "\", \"arrivalTime\":\"" + str(650) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B4" + "\", \"arrivalTime\":\"" + str(655) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "ER" + "\", \"arrivalTime\":\"" + str(660) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A1" + "\", \"arrivalTime\":\"" + str(670) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A2" + "\", \"arrivalTime\":\"" + str(700) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A3" + "\", \"arrivalTime\":\"" + str(800) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "A4" + "\", \"arrivalTime\":\"" + str(850) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B1" + "\", \"arrivalTime\":\"" + str(860) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B2" + "\", \"arrivalTime\":\"" + str(870) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B3" + "\", \"arrivalTime\":\"" + str(900) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "B4" + "\", \"arrivalTime\":\"" + str(950) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)
data = {
            "behavior": "fork_running",
            "url": "https://cpee.org/hub/server/Teaching.dir/Prak.dir/Challengers.dir/Daniel_Meierkord.dir/main.xml",
            "init": "{\"patientType\":\"" + "ER" + "\", \"arrivalTime\":\"" + str(960) + "\"}"
            }
        
response = requests.post("https://cpee.org/flow/start/url/", data = data)