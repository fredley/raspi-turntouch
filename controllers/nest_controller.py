import json
import logging
import nest
import os

# You must register for a Nest Developer account to obtain these
# Instructions are at https://github.com/jkoelker/python-nest

client_id = os.environ.get("NEST_CLIENT_ID")
client_secret = os.environ.get("NEST_CLIENT_SECRET")


logger = logging.getLogger('nest_controller')

class NestController:

    def __init__(self):
        if not client_secret or not client_id:
            logger.error("Nest Developer Account required: see https://console.developers.nest.com/developer/new")
            logger.error("Update this file with client_id and client_secret to connect to Nest")
            raise Exception("No Nest Developer Credentials")
        self.api = nest.Nest(client_id=client_id,
                client_secret=client_secret,
                access_token_cache_file='.nestauthorization')
        if self.api.authorization_required:
            logger.info("Nest is not authorized...")
            self.authenticate()
        else:
            logger.info("Connected to Nest!")

    def authenticate(self):
        logger.warn("Go to {} to authorize Nest, then enter PIN below".format(self.api.authorize_url))
        pin = input("PIN: ")
        self.api.request_token(pin)

    def print_all(self):
        for structure in self.api.structures:
            logger.info("Structure: {} ({})".format(structure.name, structure.away))
            for device in structure.thermostats:
                logger.info("  Device: {} is in mode {} at {} degrees".format(
                    device.name,
                    device.mode,
                    device.target))

    def perform(self, action):
        if action.get('structure', False):
            for s in self.api.structures:
                if s.name == action['name']:
                    structure = s
                    break
        else:
            structure = self.api.structures[0]
        if action['action'] == 'set_away':
            structure.away = 'away' if action['away'] else 'home'
            logger.info("Set {} to {}".format(structure.name, structure.away))
        if action.get('device', False):
            for d in structure.thermostats:
                if d.name == action['device']:
                    device = d
                    break
        else:
            device = structure.thermostats[0]
        if action['action'] == 'set_temp':
            device.target = action['temperature']
            logger.info("Set temperature to {}".format(device.target))
        elif action['action'] == 'adjust_temp':
            device.target = device.target + (1 if action['direction'] == 'up' else -1)
            logger.info("Set temperature to {}".format(device.target))


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler())
    n = NestController()
    n.print_all()
