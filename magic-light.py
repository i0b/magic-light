#!/usr/bin/env python2
import json, threading
from neopixel import Color
import mysensors, neopixel_control, gpio
from flask import Flask, jsonify, render_template, request
from flask.ext.socketio import SocketIO, send, emit
#from flask import copy_current_request_context

SENSOR_UPDATE_INTERVAL = 5

#database set with default values
data = {"color": "000000", 
        "element": "staticColor-000000", 
        "sensors": [{"sensorId": 0, "sensorType": 23, "sensorDescription": "Light", "sensorValue": 0}, 
                    {"sensorId": 1, "sensorType": 0, "sensorDescription": "Temperature", "sensorValue": 0}, 
                    {"sensorId": 2, "sensorType": 1, "sensorDescription": "Humidity", "sensorValue": 0}], 
        "relays": {"uplight": "off"}}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKey!'
socketio = SocketIO(app)


def startUpdateSensorValuesWorker():
  newSensorValues = mysensors.update()
  if newSensorValues is IOError:
    mysensors.stop()
    mysensors.start()
  elif newSensorValues:
    for sensor in data['sensors']:
      for newSensorValue in newSensorValues:
        if sensor['sensorId'] == newSensorValue['sensorId'] and sensor['sensorType'] == newSensorValue['sensorType']:
          data['sensors'][newSensorValue['sensorId']]['sensorValue'] = newSensorValue['sensorValue']
    updateWebClients('sensors', newSensorValues)
  threading.Timer(SENSOR_UPDATE_INTERVAL, startUpdateSensorValuesWorker).start()

# update clients with new data using socket.io
def updateWebClients(service, payload):
  if service == 'mode':
    socketio.emit('setUi', {"element": data['element'], "color": data['color'], "relays": data['relays']}, namespace='/socketio')
  elif service == 'sensors':
    socketio.emit('setSensorValues', payload, namespace='/socketio')


@app.route('/')
def index():
  return render_template('index.html')

@app.route('/sensors', methods=['GET'])
def get_sensor_data():
  return jsonify(sensors=data['sensors'])

@app.route('/wall/on', methods=['GET'])
def wall_route_on():
  try:
    percent = int(request.args.get('p'))
    if ( percent >= 0 and percent <= 100 ):
      intensity = int(percent*255.0/100.0)
      neopixel_control.oneColor(Color(intensity, intensity, intensity))
    else:
      neopixel_control.oneColor(Color(255, 255, 255))
  except:
    neopixel_control.oneColor(Color(255, 255, 255))
  return "ok"

@app.route('/wall/off')
def wall_route_off():
  neopixel_control.oneColor(Color(0, 0, 0))
  return "ok"

@app.route('/wall/rainbow')
def wall_route_rainbow():
  neopixel_control.rainbowCycleThreaded()
  return "ok"

@app.route('/wall/color/', methods=['GET'])
def color():
  try:
    red =   int ( request.args.get('r') )
    green = int ( request.args.get('g') )
    blue =  int ( request.args.get('b') )
    neopixel_control.oneColor(Color(red,green,blue))
    return "OK"
  except:
    return "There was an error changing the color."

@app.route('/uplight/on')
def uplight_route_on():
  mysensors.uplightOn()
  data['relays']['uplight'] = "on"
  updateWebClients('mode', data)
  return "on"

@app.route('/uplight/off')
def uplight_route_off():
  mysensors.uplightOff()
  data['relays']['uplight'] = "off"
  updateWebClients('mode', data)
  return "off"


@socketio.on('connect', namespace='/socketio')
def magic_connect():
  print 'client socket connected'
  emit('setUi', {"element": data['element'], "color": data['color'], "relays": data['relays']})
  emit('setSensorValues', data['sensors'])

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
          mysensors.uplightOn()
        elif (message['state'] == "off"):
          mysensors.uplightOff()
        if 'relay' in message:
          data['relays'][message['relay']] = message['state'];

    elif mode == "rainbow":
      neopixel_control.rainbow()

    elif mode == "rainbowCycle":
      neopixel_control.rainbowCycleThreaded()

    else:
      color = message['color']
      color = color.lstrip('#')
      lv = len(color)
      rgbColor = tuple(int(color[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

      if mode == "staticColor":
        neopixel_control.oneColor(Color(rgbColor[0], rgbColor[1], rgbColor[2]))

      elif mode == "colorWheel":
        neopixel_control.theaterChaseThreaded(Color(rgbColor[0], rgbColor[1], rgbColor[2]))
    updateWebClients('mode', data)
  except:
    print "ERROR: updating the magic light failed"


if __name__ == "__main__":
  neopixel_control.start()
  mysensors.start()
  startUpdateSensorValuesWorker()

  socketio.run(app, host='0.0.0.0', port=80)

# -*- coding: utf-8 -*-
