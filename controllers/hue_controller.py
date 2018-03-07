import json
import logging
from qhue import Bridge, create_new_username
import requests
import sys

from .base_controller import BaseController

class HueController(BaseController):

    def init(self, *args, **kwargs):
        try:
            with open('.hueusername') as f:
                bridge_data = json.loads(f.read())
        except:
            self.log("Bridge not authorised, need to press the button!", logging.WARN)
            bridge_data = json.loads(
                requests.get('https://www.meethue.com/api/nupnp').text)[0]
            bridge_data['username'] = create_new_username(
                    bridge_data['internalipaddress'])
            with open('.hueusername', 'w') as f:
                f.write(json.dumps(bridge_data))
        self.bridge = Bridge(bridge_data['internalipaddress'], bridge_data['username'])
        self.log("Successfully connected to Hue Bridge {}".format(bridge_data['internalipaddress']))

    def print_all(self):
        self.log("Lights:")
        for room_id, room in self.bridge.groups().items():
            self.log("{} [ID: {}] - {}:".format(room['type'], room_id, room['name']))
            for light_id in room['lights']:
                light = self.bridge.lights()[light_id]
                self.log(" - [ID: {}]: {} ({})".format(
                    light_id, light['name'], light['type']))
            self.log(" ")
        self.log("Scenes:")
        for scene in self.bridge.scenes().values():
            self.log(" - {}".format(scene['name']))

    def set_light(self, id, *args, **kwargs):
        self.log("Setting light {}: {}".format(id, kwargs))
        self.bridge.lights[id].state(**kwargs)

    def set_room(self, id, *args, **kwargs):
        self.log("Setting room {}: {}".format(id, kwargs))
        self.bridge.groups[id].state(**kwargs)

    def adjust_light_brightness(self, id, *args, **kwargs):
        current_amount = self.bridge.lights[id]['brightness']
        if kwargs['direction'] == 'up':
            new_amount = current_amount + kwargs.get('amount', 16)
        else:
            new_amount = current_amount - kwargs.get('amount', 16)
        self.set_light(id, **{'brightness': new_amount})

    def set_scene(self, id, *args, **kwargs):
        scene_id = [k for k, v in self.bridge.scenes().items() if v['name'] == kwargs['scene']]
        self.bridge.groups[id].state({'scene': scene_id})

    def perform(self, action):
        kwargs = {k: v for k, v in action.items() if k not in ['action', 'id', 'type']}
        id, act = action['id'], action['action']
        if act == 'set_light':
            self.set_light(id, **kwargs)
        elif act == 'set_room':
            self.set_room(id, **kwargs)
        elif act == 'adjust_brightness':
            pass
        elif act == 'set_scene':
            self.set_scene(id, **kwargs)

    @classmethod
    def help(cls):
      return """
Hue Module - Control Hue Lights

Usage:

north_press:
  type: hue
  action: set_light
  id: 1                      # See below for IDs
  bri: 254                   # From 1 to 254
  hue: 9000                  # From 0 to 65535, hardware dependent

north_press:
  type: hue
  action: set_room
  id: 1                      # See below for IDs
  bri: 254                   # From 1 to 254
  hue: 9000                  # From 0 to 65535, hardware dependent

north_press:
  type: hue
  action: adjust_brightness
  id: 1                      # Light ID. See below for IDs
  direction: up              # or down

north_press:
  type: hue
  action: set_scene
  id: 1                      # Room ID. See below for IDs
  scene: Scene Name          # see below
"""
