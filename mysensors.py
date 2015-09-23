import re, socket

def start():
  HOST = '192.168.178.166'
  PORT = 5003

  global gatewaysocket
  gatewaysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  gatewaysocket.connect((HOST, PORT))

def stop():
  gatewaysocket.close()

def update():
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
    return False

def uplightOn():
  COMMAND = "20;3;1;0;2;0\n"
  gatewaysocket.send(COMMAND)

def uplightOff():
  COMMAND = "20;3;1;0;2;1\n"
  gatewaysocket.send(COMMAND)

if __name__ == '__main__':
  startGateway()
