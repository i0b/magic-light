#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import threading
import json
from flask import Flask, jsonify, render_template, request
from flask import copy_current_request_context
from flask.ext.socketio import SocketIO, send, emit
from neopixel import *
from neopixel_animations import *
from mysensors import *
from gpio import *
from threading import Thread
from threading import Event


# LED strip configuration:
LED_COUNT   = 240     # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

SENSOR_UPDATE_INTERVAL = 5

data = {"color": "000000", "element": "staticColor-000000", "sensors": [{"sensorId": 0, "sensorType": 23, "sensorValue": 0}, {"sensorId": 1, "sensorType": 0, "sensorValue": 0}, {"sensorId": 2, "sensorType": 1, "sensorValue": 0}], "relays": {"uplight": "off"}}

threads = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def startFetchAndUpdateSensorValues():
  sensorValues = updateSensors()
  if sensorValues:
    updateSensorValues(sensorValues)
    updateAll('sensors', sensorValues)
  threading.Timer(SENSOR_UPDATE_INTERVAL, startFetchAndUpdateSensorValues).start()

def updateSensorValues(newSensorValues):
  for sensor in data['sensors']:
    for newSensorValue in newSensorValues:
      if sensor['sensorId'] == newSensorValue['sensorId'] and sensor['sensorType'] == newSensorValue['sensorType']:
        data['sensors'][newSensorValue['sensorId']]['sensorValue'] = newSensorValue['sensorValue']

def stopAnimations():
  while threads:
    (thread, event) = threads.pop()
    event.set()
    while thread.isAlive():
      time.sleep(1/1000.0)

def updateAll(service, payload):
  if service == 'mode':
    socketio.emit('setUi', {"element": data['element'], "color": data['color'], "relays": data['relays']}, namespace='/socketio')
    #broadcast=True, 
  elif service == 'sensors':
    socketio.emit('setSensorValues', payload, namespace='/socketio')

@app.route('/')
def index():
  return render_template('index.html')

@socketio.on('update', namespace='/socketio')
def magic_update(message, namespace):
  try:
    if 'mode' in message and 'element' in message:
      mode = message['mode']
      if mode == "staticColor" or mode == "colorWheel" or mode == "rainbow" or mode == "rainbowCycle":
        data['element'] = message['element']
    else:
      return

    if 'color' in message:
      data['color'] = message['color']
    else:
      data['color'] = "none"

    if mode == "setGPIO":
      if 'pin' in message and 'pinValue' in message:
        setGPIO(message.pin, message.pinValue)

    elif mode == "power":
      if 'state' in message:
        if (message['state'] == 'on'):
          uplightOn()
        elif (message['state'] == "off"):
          uplightOff()
        if 'relay' in message:
          data['relays'][message['relay']] = message['state'];

    elif mode == "rainbow":
      stopAnimations()
      rainbow(strip)

    elif mode == "rainbowCycle":
      stopAnimations()
      interrupt = Event()
      thread = Thread(target=rainbowCycle, args=(interrupt, strip,))
      threads.append((thread, interrupt))
      thread.start()

    else:
      color = message['color']
      currentColor = color
      rgbColor = hex_to_rgb (color)

      if mode == "staticColor":
        stopAnimations()
        oneColor(strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]))
      elif mode == "colorWheel":
        stopAnimations()
        interrupt = Event()
        thread = Thread(target=theaterChase, args=(interrupt, strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]),))
        threads.append((thread, interrupt))
        thread.start()
    updateAll('mode', data)
  except:
    print "ERROR: updating the magic light failed"

@socketio.on('connect', namespace='/socketio')
def magic_connect():
  emit('setUi', {"element": data['element'], "color": data['color'], "relays": data['relays']})
  emit('setSensorValues', data['sensors'])

@app.route('/sensors')
def get_sensor_data():
  return jsonify(sensors=data['sensors'])

@app.route('/wall/on', methods=['GET'])
def wall_route_on():
  stopAnimations()
  try:
    percent = int ( request.args.get('p') )
    if ( percent >= 0 and percent <= 100 ):
      colorVal = int (percent*255.0/100.0)
      oneColor(strip, Color(colorVal, colorVal, colorVal))
    else:
      oneColor(strip, Color(255, 255, 255))
  except:
    oneColor(strip, Color(255, 255, 255))
  return "on"

@app.route('/wall/off')
def wall_route_off():
  stopAnimations()
  oneColor(strip, Color(0, 0, 0))
  return "off"

@app.route('/wall/color/', methods=['GET'])
def color():
  stopAnimations()
  try:
    red =   int ( request.args.get('r') )
    green = int ( request.args.get('g') )
    blue =  int ( request.args.get('b') )
    oneColor(strip, Color(red,green,blue))
    return "OK"
  except:
    return "There was an error changing the color."

@app.route('/uplight/on')
def uplight_route_on():
  uplightOn()
  data['relays']['uplight'] = "on"
  updateAll('mode', data)
  return "on"

@app.route('/uplight/off')
def uplight_route_off():
  uplightOff()
  data['relays']['uplight'] = "off"
  updateAll('mode', data)
  return "off"

if __name__ == "__main__":
  try:
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
    # Intialize the library (must be called once before other functions).
    strip.begin()
  except:
    exit(1)

  startGateway()
  startFetchAndUpdateSensorValues()

  socketio.run(app, host='0.0.0.0', port=80)
  #app.run(host='0.0.0.0', port=80, debug=True)

# -*- coding: utf-8 -*-
