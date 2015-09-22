import fcntl, os, subprocess, time, re, serial

def startGateway():
  global gatewayprocess
  gatewayprocess = subprocess.Popen(['PiGatewaySerial'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  fcntl.fcntl(gatewayprocess.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

def stopGateway():
  subprocess.call(["killall", "GatewaySerial"])

def updateSensors():
  processoutput = ''
  try:
    processoutput = gatewayprocess.stdout.read()
  except IOError:
    pass

  if "read:" in processoutput:
    sensorupdates = []
    for line in processoutput.split('\n'):
      try:
        (s, c, t, pt, l, v) = [t(s) for t,s in zip((int,int,int,int,int,float),re.search('read: 20-20-0 s=(\d+),c=(\d+),t=(\d+),pt=(\d+),l=(\d+):([\d.]+)$',line).groups())]
        data = {"sensorId": s, "sensorType": t, "sensorValue": v}
        try:
          index = next(index for (index, d) in enumerate(sensorupdates) if d["sensorId"] == s)
          sensorupdates[index] = data
        except StopIteration:
          sensorupdates.append(data)
      except AttributeError:
        #print("ERR: ", line)
        pass
    return sensorupdates
  else:
    return False

def uplightOn():
  serialConnection = serial.Serial('/dev/ttyMySensorsGateway', 9600)
  serialConnection.write('20;3;1;0;2;0\n')

def uplightOff():
  serialConnection = serial.Serial('/dev/ttyMySensorsGateway', 9600)
  serialConnection.write('20;3;1;0;2;1\n')

if __name__ == '__main__':
  startGateway()
