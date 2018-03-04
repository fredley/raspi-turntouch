from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import gatt
import yaml
import subprocess

from controllers.hue_controller import HueController
from controllers.nest_controller import NestController

manager = gatt.DeviceManager(adapter_name='hci0')


class TurnTouch(gatt.Device):

    button_codes = {
        b'\xff\x00': 'Off',
        b'\xfe\x00': 'North Press',
        b'\xef\x00': 'North Double',
        b'\xfe\xff': 'North Hold',
        b'\xfd\x00': 'East Press',
        b'\xdf\x00': 'East Double',
        b'\xfd\xff': 'East Hold',
        b'\xfb\x00': 'West Press',
        b'\xbf\x00': 'West Double',
        b'\xfb\xff': 'West Hold',
        b'\xf7\x00': 'South Press',
        b'\x7f\x00': 'South Double',
        b'\xf7\xff': 'South Hold'
    }

    button_presses = []

    battery_notifications_sent = []

    def __init__(self, mac_address, manager, buttons, name, controllers):
        super().__init__(mac_address, manager)
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.button_actions = buttons
        self.listening = False
        self.name = name
        self.controllers = controllers

    def connect_succeeded(self):
        super().connect_succeeded()
        print("Connected!")

    def connect_failed(self, error):
        super().connect_failed(error)
        print("Connect failed with error {}".format(error))

    def services_resolved(self):
        super().services_resolved()
        button_status_service = next(s for s in self.services
                if s.uuid == '99c31523-dc4f-41b1-bb04-4e4deb81fadd')

        self.button_status_characteristic = next(c for c in button_status_service.characteristics
                if c.uuid == '99c31525-dc4f-41b1-bb04-4e4deb81fadd')

        self.button_status_characteristic.enable_notifications()

        battery_status_service = next(s for s in self.services
                if s.uuid.startswith('0000180f'))

        self.battery_status_characteristic = next(c for c in battery_status_service.characteristics
                if c.uuid.startswith('00002a19'))

        self.battery_status_characteristic.read_value()
        self.sched.add_job(self.battery_status_characteristic.read_value,
                trigger='interval', minutes=1) #todo: reduce this

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("Connected to {}!".format(self.name))

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
        if characteristic == self.battery_status_characteristic:
            percentage = int(int.from_bytes(value, byteorder='big') * 100/ 255)
            key = 'battery_{}'.format(percentage)
            if self.button_actions.get(key, False) and key not in self.battery_notifications_sent:
                self.battery_notifications_sent.append(key)
                self.perform('battery', str(percentage))
            print('Battery status: {}%'.format(percentage))
            return
        if value == b'\xff\x00': #off
            return
        self.button_presses.append(value)
        if not self.listening:
            self.listening = True
            time = datetime.datetime.now() + datetime.timedelta(seconds=1)
            self.sched.add_job(self.deduplicate_buttons, trigger='date', run_date=time)

    def deduplicate_buttons(self):
        self.listening = False
        actions = [self.button_codes[p] for p in self.button_presses]
        # work out what to do
        first_words = [s.split(' ')[0] for s in actions]
        second_words = [s.split(' ')[1] for s in actions]
        self.button_presses = []
        if len(set(first_words)) != 1:
            print("Too many presses too quickly")
            return
        direction = first_words[0]
        if 'Double' in second_words:
            self.perform(direction, 'Double')
        elif 'Hold' in second_words:
            self.perform(direction, 'Hold')
        else:
            self.perform(direction, 'Press')

    def perform(self, direction, action):
        print("Performing {} {}".format(direction, action))
        action = self.button_actions.get("{}_{}".format(direction.lower(), action.lower()), {'type': 'none'})
        if action['type'] == 'none':
            return
        elif action['type'] == 'bash':
            try:
                print(
                        subprocess.check_output(action['command'], shell=True
                ).decode('utf-8').strip())
            except Exception as e:
                print("Something went wrong: {}".format(e))
        elif action['type'] in self.controllers:
            self.controllers[action['type']].perform(action)
        else:
            print("No controller found for action {}".format(action['type']))

if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            config = yaml.load(f)
            print('Config loaded: {}'.format(config))
    except Exception as e:
        config = []
        print("Error loading config: {}".format(e))
    for c in config:
        types = [b['type'] for _, b in c['buttons'].items()]
        controllers = {}
        if 'hue' in types:
            print("Loading Hue...")
            controllers['hue'] = HueController()
        if 'nest' in types:
            print("Loading Nest...")
            controllers['nest'] = NestController()
        else:
            hue_controller = None
        device = TurnTouch(
                mac_address=c['mac'],
                manager=manager,
                buttons=c['buttons'],
                name=c['name'],
                controllers=controllers
        )
        print("Trying to connect to {} at {}...".format(c['name'], c['mac']))
        device.connect()
    manager.run()
