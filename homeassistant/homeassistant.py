#!/usr/bin/env python
import time
from selfdrive import messaging
from selfdrive.services import service_list
import requests
import subprocess

# Run me via openpilot's manager.py.
# Append me to the managed processes list on line 71 and and also persistent_processes at line 113 of manager.py

# TODO: externalize this
# To get an auth token for you device, go into HA and click on your avatar (first letter of your username if no picture) to get to your profle, then scroll down to make a long life token. It only appears once, so put it somewhere safe
AUTH_TOKEN = ''
# the url and what you want to call your EON entity. ie, 'https://myhomeassistanturl.com/api/states/eon.chris'
API_URL = 'https://myhomeassistanturl.com/api/states/eon.chris'
# where you want to ping before attemtping a send. probably your 'myhomeassistanturl.com' url
PING_URL = 'myhomeassistanturl.com'


class Data:
  def __init__(self):
    # socks
    self.location = messaging.sub_sock(service_list['gpsLocation'].port)
    self.health = messaging.sub_sock(service_list['health'].port)
    self.thermal = messaging.sub_sock(service_list['thermal'].port)

    # time management
    self.fast_mode = False
    self.last_read = 0
    self.last_send = 0

    if self.fast_mode:
      self.time_to_read = 0.1
      self.time_to_send = 1
    else:
      self.time_to_read = 59
      self.time_to_send = 60

    # gpsLocation
    self.latitude = -1
    self.longitude = -1
    self.altitude = -1
    self.speed = -1
    # health
    self.car_voltage = -1
    # thermal
    self.eon_soc = -1
    self.bat_temp = -1
    self.usbonline = None
    self.started = None

  def read(self):
    # TODO: refactor the try/excepts to gracefully fail

    """Read the data from the zmq sockets."""
    try:
      location_sock = messaging.recv_sock(self.location)
      if location_sock is not None:
        self.latitude = round(location_sock.gpsLocation.latitude, 6)
        self.longitude = round(location_sock.gpsLocation.longitude, 6)
        self.altitude = round(location_sock.gpsLocation.altitude, 2)
        self.speed = round(location_sock.gpsLocation.speed, 2)
    except:
      print("Location sock failed")

    # the health packet is only sent every so often
    try:
      health_sock = messaging.recv_sock(self.health)
      if health_sock is not None:
        self.car_voltage = health_sock.health.voltage
    except:
      print("Health sock failed")

    # TODO: do we actually need to wait?
    try:
      thermal_sock = messaging.recv_sock(self.thermal, wait=True)
      if thermal_sock is not None:
        self.eon_soc = thermal_sock.thermal.batteryPercent
        self.bat_temp = round(thermal_sock.thermal.bat * .001, 2)
        self.usbonline = thermal_sock.thermal.usbOnline
        self.started = thermal_sock.thermal.started
    except:
      print("Thermal sock failed")
    self.last_read = time.time()
    return

  def send(self):
    """Send the data collected from the zmq sockets to homeassistant."""
    # if the ping is good, continue. else, wait and try again
    while 1:
      ping = subprocess.call(["ping", "-W", "4", "-c", "1", PING_URL])
      if ping:
        # didn't get a good ping. sleep and try again
        time.sleep(5)
      else:
        break

    self.time_sent = time.ctime()

    # we have to add 'Bearer ' to the header string. yes, the space after Bearer is necessary
    token_string = 'Bearer ' + AUTH_TOKEN

    headers = {
    'Authorization': token_string,
    'content-type': 'application/json',
    }
    stats = {'latitude': self.latitude,
    'longitude': self.longitude,
    'altitude': self.altitude,
    'speed': self.speed,
    'car_voltage': self.car_voltage,
    'eon_soc': self.eon_soc,
    'bat_temp': self.bat_temp,
    'usb_online': self.usbonline,
    'started': self.started
    }
    data = {'state': self.time_sent,
    'attributes': stats,
    }

    # try to send. if sending doesn't work, return and wait until the next time around
    try:
      self.last_send = time.time()
      r = requests.post(API_URL, headers=headers, json=data)
      if not r.status_code == requests.codes.ok:
        print("Problem sending. Retry")
    except:
      print("Sending totally failed")
    return


def main(gctx=None):
  # init the whole thing
  data = Data()

  # loop the thing
  while 1:
    time_now = time.time()
    # read every n seconds
    if time_now - data.last_read >= data.time_to_read:
      data.read()
      time_now = time.time()
    # send ever n seconds
    if time_now - data.last_send >= data.time_to_send:
      data.send()
      time_now = time.time()
    time.sleep(1)


if __name__ == '__main__':
  main()
