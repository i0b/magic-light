from neopixel import *
from threading import Event
from threading import Thread
import datetime
import time

threads = []

# LED strip configuration:
LED_COUNT   = 240     # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

default_strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)


#--------------------------------------------------------------------------------------

def oneColor(color, strip=default_strip):
  """One color without delay."""
  stopAnimation()
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

def colorWipe(e, color, wait_ms=50, strip=default_strip):
  """Wipe color across display a pixel at a time."""
  stopAnimation()
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms/1000.0)

def theaterChase(e, color, wait_ms=50, strip=default_strip):
  """Movie theater light style chaser animation."""
  while not e.isSet():
    for j in range(3):
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+j, color)
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+j, 0)

def theaterChaseThreaded(color):
  stopAnimation()
  interrupt = Event()
  thread = Thread(target=theaterChase, args=(interrupt, color,))
  threads.append((thread, interrupt))
  thread.start()

def rainbow(strip=default_strip):
  """Draw rainbow that fades across all pixels at once."""
  stopAnimation()
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, wheel(i))
  strip.show()

def rainbowCycle(e, wait_ms=50, strip=default_strip):
  """Draw rainbow that uniformly distributes itself across all pixels."""
  j=0
  while not e.isSet():
    j=j+1
    for i in range(strip.numPixels()):
      strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
    strip.show()
    time.sleep(wait_ms/1000.0)

def rainbowCycleThreaded():
  stopAnimation()
  interrupt = Event()
  thread = Thread(target=rainbowCycle, args=(interrupt,))
  threads.append((thread, interrupt))
  thread.start()

def theaterChaseRainbow(e, wait_ms=50, strip=default_strip):
  """Rainbow movie theater light style chaser animation."""
  stopAnimation()
  for j in range(256):
    for q in range(3):
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, wheel((i+j) % 255))
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, 0)

#--------------------------------------------------------------------------------------

def wheel(pos):
  """Generate rainbow colors across 0-255 positions."""
  if pos < 85:
    return Color(pos * 3, 255 - pos * 3, 0)
  elif pos < 170:
    pos -= 85
    return Color(255 - pos * 3, 0, pos * 3)
  else:
    pos -= 170
    return Color(0, pos * 3, 255 - pos * 3)

def start():
  default_strip.begin()

def stopAnimation():
  while threads:
    (thread, event) = threads.pop()
    event.set()
    while thread.isAlive():
      time.sleep(1/1000.0)

#--------------------------------------------------------------------------------------

if __name__ == "__main__":
  start()

# -*- coding: utf-8 -*-
