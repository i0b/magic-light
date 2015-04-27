from neopixel import *
from threading import Event
import datetime
import time


# Define functions which animate LEDs in various ways.
def oneColor(strip, color):
  """One color without delay."""
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
  strip.show()

def colorWipe(e, strip, color, wait_ms=50):
  """Wipe color across display a pixel at a time."""
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, color)
    strip.show()
    time.sleep(wait_ms/1000.0)

def theaterChase(e, strip, color, wait_ms=50):
  """Movie theater light style chaser animation."""
  while not e.isSet():
    for j in range(3):
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+j, color)
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+j, 0)

def rainbow(e, strip):
  """Draw rainbow that fades across all pixels at once."""
  for i in range(strip.numPixels()):
    strip.setPixelColor(i, wheel(i))
  strip.show()

def rainbowCycle(e, strip, wait_ms=50):
  """Draw rainbow that uniformly distributes itself across all pixels."""
  j=0
  while not e.isSet():
    j=j+1
    for i in range(strip.numPixels()):
      strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
    strip.show()
    time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(e, strip, wait_ms=50):
  """Rainbow movie theater light style chaser animation."""
  for j in range(256):
    for q in range(3):
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, wheel((i+j) % 255))
      strip.show()
      time.sleep(wait_ms/1000.0)
      for i in range(0, strip.numPixels(), 3):
        strip.setPixelColor(i+q, 0)


#//////////////////////////////////////////////////////////////////////////////////////

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

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

# -*- coding: utf-8 -*-
