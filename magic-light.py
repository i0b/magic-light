#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import json
from flask import Flask, jsonify, render_template, request
from flask.ext.socketio import SocketIO
from flask.ext.socketio import emit
from neopixel import *
from neopixel_animations import *
from threading import Thread
from threading import Event


# LED strip configuration:
LED_COUNT   = 240     # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

data = {"color": "000000", "element": "staticColor-000000"}
threads = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def stopAnimations():
  while threads:
    (thread, event) = threads.pop()
    event.set()
    while thread.isAlive():
      time.sleep(1/1000.0)

def updateAll():
  emit('setUi', {"element": data['element']}, broadcast=True)

@app.route('/')
def index():
  return render_template('index.html')

@socketio.on('update', namespace='/socketio')
def magic_update(message, namespace):
  try:
    if 'mode' in message and 'element' in message:
      mode = message['mode']
      data['element'] = message['element']
    else:
      rainbow(strip)
      return

    if 'color' in message:
      data['color']   = message['color']
    else:
      data['color']   = "none"

    if mode == "rainbow":
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
    updateAll()
  except:
    print "ERROR: updating the magic light failed"

@socketio.on('connect', namespace='/socketio')
def magic_connect():
  emit('setUi', {"element": data['element']})

@app.route('/on', methods=['GET'])
def on():
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

@app.route('/off')
def off():
  stopAnimations()
  oneColor(strip, Color(0, 0, 0))
  return "off"

@app.route('/color/', methods=['GET'])
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


if __name__ == "__main__":
  try:
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
    # Intialize the library (must be called once before other functions).
    strip.begin()
  except:
    exit(1)

  socketio.run(app, host='0.0.0.0', port=80)
  #app.run(host='0.0.0.0', port=80, debug=True)

# -*- coding: utf-8 -*-
