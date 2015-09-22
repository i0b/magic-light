import RPi.GPIO as GPIO

def setGPIO(pin, value):
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(pin, GPIO.OUT)

  if value == "LOW":
    GPIO.output(pin, GPIO.LOW)
  elif value == "HIGH":
    GPIO.output(pin, GPIO.HIGH)

  GPIO.cleanup()
