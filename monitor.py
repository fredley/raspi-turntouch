from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import gatt
import yaml
import subprocess


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

    def __init__(self, mac_address, manager, buttons, name):
        super().__init__(mac_address, manager)
        self.sched = BackgroundScheduler()
        self.sched.start()
        self.button_actions = buttons
        self.listening = False
        self.name = name

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

        button_status_characteristic = next(c for c in button_status_service.characteristics
                if c.uuid == '99c31525-dc4f-41b1-bb04-4e4deb81fadd')

        button_status_characteristic.enable_notifications()

    def characteristic_enable_notifications_succeeded(self, characteristic):
        super().characteristic_enable_notifications_succeeded(characteristic)
        print("Connected to {}!".format(self.name))

    def characteristic_value_updated(self, characteristic, value):
        super().characteristic_value_updated(characteristic, value)
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
        try:
            print(subprocess.check_output(
                self.button_actions.get(
                    "{}_{}".format(direction.lower(), action.lower()), 'echo "No action specified"'),
                shell=True
            ).decode('utf-8').strip())
        except Exception as e:
            print("Something went wrong: {}".format(e))


if __name__ == '__main__':
    try:
        with open('config.yml') as f:
            config = yaml.load(f)
            print('Config loaded: {}'.format(config))
    except Exception as e:
        config = []
        print("Error loading config: {}".format(e))
    for c in config:
        device = TurnTouch(mac_address=c['mac'], manager=manager, buttons=c['buttons'], name=c['name'])
        print("Trying to connect to {} at {}...".format(c['name'], c['mac']))
        device.connect()
    manager.run()
