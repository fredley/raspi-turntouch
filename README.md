# Turn Touch Raspberry Pi Client

## Installation

This code was written and tested with a Raspberry Pi Zero W.

Assuming python3 and pip3 are installed, install the following **as root**. Do not use a virtualenv!

```bash
sudo pip3 install gatt pyyaml apscheduler qhue python-nest
sudo apt-get install python3-dbus
```

Make sure your Turn Touch is disconnected **and unpaired** from any other devices, then run:

```sudo gattctl --discover```

You should see the Turn Touch come up and see its MAC Address, which will look similar to `c2:51:f2:36:3f:ad`.

Put this mac address in config.yml, and update any button press options you would like to configure - just enter any bash script to run.

Launch the listener with:

```sudo python3 monitor.py```

It should connect, and once it has you should be able to press buttons on your Turn Touch and see the output of your commands.


## Hue Controller

In order to connect to your Hue Bridge, it's easest to run setup separately first:

```python3 controllers/hue_controller.py```

This will prompt you to press the button on your bridge, then list out your lights, by id, type and room.
You can then configure button presses in `config.yml` as follows:

```yaml
north_double:
    type: hue
    id: 1 # From output of python3 hue.py
    brightness: # 1-254
    hue: 9000 # From 0 to 65535, hardware dependent
```

Setting scenes, or rooms is not possible, yet!

## Nest Controller

In order to connect to your Nest, you need to register for a Nest Developer account, and get a product ID and secret, which you must insert into `controllers/nest_controller.py` manually.

Then, you can authenticate yourself by running:

```python3 controllers/nest_controller.py```

This will give you a URL, which will give you a PIN which you will be prompted for. If successful, the controller will then print out all homes and devices. You can then configure your remote using the following:

```yaml
east_press:
    type: nest
    structure: My Home # As in listed values. Can be omitted if only one structure
    device: Kitchen # As in listed values. Can be omitted if only one device
    action: adjust_temp
    temperature: 18 # will be ºF or ºC as per the settings on your nest. Just put in the right number.
east_double:
    type: nest
    action: adjust_temp
    direction: up # will add 1º to the target temp, or use 'down' for -1º
east_hold:
    type: nest
    action: set_away
    away: true # Sets your device to away, or use false to set home
```

Currently, only nest thermostats are supported, and again no room support.

## Battery Status

The battery status is checked every hour. If you would like something to happen when it falls below a certain value, use the following:

```yaml
battery_10: # will trigger when batter falls to 10%
    type: bash
    command: email_me.sh
```
