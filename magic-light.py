#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
import json
from flask import Flask, jsonify, render_template, request
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

filename = '/srv/magic-light/data'
data = {}
with open(filename, 'r') as infile:
  data = json.load(infile)

activeElement = data['element']
activeColor   = data['color']
threads = []

app = Flask(__name__)

def stopAnimations():
  while threads:
    (thread, event) = threads.pop()
    event.set()
    while thread.isAlive():
      time.sleep(1/1000.0)

@app.route('/')
def index():
  stopAnimations()

  try:
    mode = request.args.get('mode')
    if mode == "static-color":
      color = request.args.get('color')
      currentColor = color
      rgbColor = hex_to_rgb (color)
      oneColor(strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]))
    elif mode == "color-wheel":
      color = request.args.get('color')
      currentColor = color
      rgbColor = hex_to_rgb (color)
      interrupt = Event()
      thread = Thread(target=theaterChase, args=(interrupt, strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]),))
      threads.append((thread, interrupt))
      thread.start()
    elif mode == "rainbow":
      rainbow(strip)
    elif mode == "rainbowCycle":
      interrupt = Event()
      thread = Thread(target=rainbowCycle, args=(interrupt, strip,))
      threads.append((thread, interrupt))
      thread.start()
  except:
    print "no valid mode given"

  return render_template('index.html')

@app.route('/_mode', methods=['POST'])
def mode():
  stopAnimations()
  try:
    mode = request.form['mode']

    if mode == "rainbow":
      rainbow(strip)
    elif mode == "rainbowCycle":
      interrupt = Event()
      thread = Thread(target=rainbowCycle, args=(interrupt, strip,))
      threads.append((thread, interrupt))
      thread.start()
    else:
      color = request.form['color']
      currentColor = color
      rgbColor = hex_to_rgb (color)

      if mode == "staticColor":
        oneColor(strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]))
        ret_data = {"status": "OK"}
      elif mode == "colorWheel":
        interrupt = Event()
        thread = Thread(target=theaterChase, args=(interrupt, strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]),))
        threads.append((thread, interrupt))
        thread.start()
        ret_data = {"status": "OK"}
  except:
    ret_data = {"status": "ERROR"}

  return jsonify(ret_data)

@app.route('/_state', methods=['GET', 'POST'])
def state():
  global activeElement
  global activeColor

  if request.method == 'POST':
    try:
      if request.form['element']:
        data['element'] = request.form['element']
        activeElement   = request.form['element']

        if request.form['color']:
          data['color']   = request.form['color']
          activeColor     = request.form['color']
        else:
          data['color']   = 'none'
          activeColor     = 'none'

        with open(filename, 'w') as outfile:
          json.dump(data, outfile)

        ret_data = {"status": "OK"}
      else:
        ret_data = {"status": "WRONG ARGUMENTS ERROR"}
    except:
      ret_data = {"status": "PARSING ERROR"}
    return jsonify(ret_data)
#  if request.method == 'POST' or request.method == 'PUT':
#    fetchedData = jsonify(request.get_json(force=True))
#    try:
#      data['element'] = fetchedData['element']
#      data['color']   = fetchedData['color']
#      with open(filename, 'w') as outfile:
#        json.dump(data, outfile)
#      ret_data = {"status": "OK"}
#    except:
#      ret_data = {"status": "DATA ERROR - format of sent data not correct"}
#    return jsonify(ret_data)
  elif request.method == 'GET':
    ret_data = {"element": activeElement, "color": activeColor}
    return jsonify(ret_data)

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

  app.run(host='0.0.0.0', port=80, debug=True)

# -*- coding: utf-8 -*-
