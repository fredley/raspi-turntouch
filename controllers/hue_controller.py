import logging
import json
from qhue import Bridge, create_new_username
import requests

logger = logging.getLogger('hue_controller')

class HueController:

    def __init__(self):
        try:
            with open('.hueusername') as f:
                bridge_data = json.loads(f.read())
        except:
            logger.warn("Bridge not authorised, need to press the button!")
            bridge_data = json.loads(
                requests.get('https://www.meethue.com/api/nupnp').text)[0]
            bridge_data['username'] = create_new_username(
                    bridge_data['internalipaddress'])
            with open('.hueusername', 'w') as f:
                f.write(json.dumps(bridge_data))
        self.bridge = Bridge(bridge_data['internalipaddress'], bridge_data['username'])
        logger.info("Successfully connected to Hue Bridge {}".format(bridge_data['internalipaddress']))

    def print_all_lights(self):
        rooms = self.bridge.groups()
        for id, light in self.bridge.lights().items():
            room = [r for r in rooms.values() if id in r['lights']]
            logger.info("[{}]: {} ({}){}".format(
                id, light['name'], light['type'],
                " in {}".format(room[0]['name']) if room else ""))

    def set_light(self, id, *args, **kwargs):
        self.bridge.lights[id].state(**kwargs)

    def perform(self, action):
        self.set_light(action['id'], bri=action['brightness'], hue=action['hue'])


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    c = HueController()
    c.print_all_lights()
