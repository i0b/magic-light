#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import time
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

threads = []
activeElement = ''
setColor = ''

app = Flask(__name__)

def stopAnimations():
  while threads:
    (thread, event) = threads.pop()
    event.set()
    while thread.isAlive():
      time.sleep(1/1000.0)

@app.route('/_getSetColor', methods=['GET'])
def getSetColor():
  ret_data = {"value": setColor }
  return jsonify(ret_data)

@app.route('/_getActiveElement', methods=['GET'])
def getActiveElement():
  ret_data = {"value": activeElement }
  return jsonify(ret_data)

@app.route('/_setActiveElement', methods=['GET'])
def setActiveElement():
  try:
    activeElement = request.args.get('activeElement')
    ret_data = {"value": "OK"}
  except:
    ret_data = {"value": "ERROR"}
    return jsonify(ret_data)

@app.route('/')
def index():
  stopAnimations()

  try:
    mode = request.args.get('mode')
    if mode == "static-color":
      color = request.args.get('color')
      setColor = color
      rgbColor = hex_to_rgb (color)
      oneColor(strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]))
    elif mode == "color-wheel":
      color = request.args.get('color')
      setColor = color
      rgbColor = hex_to_rgb (color)
      interrupt = Event()
      thread = Thread(target=theaterChase, args=(interrupt, strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]),))
      threads.append((thread, interrupt))
      thread.start()
    elif mode == "rainbow":
      interrupt = Event()
      thread = Thread(target=rainbow, args=(interrupt, strip,))
      threads.append((thread, interrupt))
      thread.start()
    elif mode == "rainbow-cycle":
      interrupt = Event()
      thread = Thread(target=rainbowCycle, args=(interrupt, strip,))
      threads.append((thread, interrupt))
      thread.start()
  except:
    print "no valid mode given"

  return render_template('index.html')

@app.route('/_setColor', methods=['GET'])
def setColor():
  stopAnimations()
  mode = request.args.get('mode')

  try:
    if mode == "static":
      color = request.args.get('color')
      setColor = color
      rgbColor = hex_to_rgb (color)
      oneColor(strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]))
      ret_data = {"value": "OK"}
    elif mode == "wheel":
      color = request.args.get('color')
      setColor = color
      rgbColor = hex_to_rgb (color)
      interrupt = Event()
      thread = Thread(target=theaterChase, args=(interrupt, strip, Color(rgbColor[0], rgbColor[1], rgbColor[2]),))
      threads.append((thread, interrupt))
      thread.start()
      ret_data = {"value": "OK"}
  except:
    ret_data = {"value": "ERROR"}

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
