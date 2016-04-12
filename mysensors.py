import re, socket

def start():
  #HOST = '192.168.178.166'
  HOST = 'ESP-F47A1C.fritz.box'
  PORT = 5003

  global gatewaysocket

  try:
    gatewaysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gatewaysocket.connect((HOST, PORT))
    print 'connected to: {0}'.format(HOST) 
  except socket.error as e:
    gatewaysocket = None
    print 'could not connect to mysensors controller'

def stop():
  if gatewaysocket is not None:
    gatewaysocket.close()

def update():
  if gatewaysocket is not None:
    print 'updating sensor values'
    try:
      sensorupdates = []
      try:
        line = gatewaysocket.makefile().readline()
        (nodeId, sensorId, messageType, ackMessage, sensorType, sensorValue) = [t(s) for t,s in zip((int,int,int,int,int,float),re.search('(\d+);(\d+);(\d+);(\d+);(\d+);([\d.]+)$',line).groups())]
        data = {"sensorId": sensorId, "sensorType": sensorType, "sensorValue": sensorValue}
        try:
          index = next(index for (index, d) in enumerate(sensorupdates) if d["sensorId"] == s)
          sensorupdates[index] = data
        except StopIteration:
          sensorupdates.append(data)
      except AttributeError:
        pass
      return sensorupdates
    except IOError:
      return IOError
  else:
    return IOError

def uplightOn():
  print 'sending command: uplight on'
  if gatewaysocket is not None:
    COMMAND = "20;3;1;0;2;0\n"
    gatewaysocket.send(COMMAND)

def uplightOff():
  print 'sending command: uplight off'
  if gatewaysocket is not None:
    COMMAND = "20;3;1;0;2;1\n"
    gatewaysocket.send(COMMAND)

if __name__ == '__main__':
  startGateway()

# -*- coding: utf-8 -*-
