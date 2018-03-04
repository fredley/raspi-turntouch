# Turn Touch Raspberry Pi Client

## Installation

This code was written and tested with a Raspberry Pi Zero W.

Assuming python3 and pip3 are installed, install the following **as root**. Do not use a virtualenv!

```
sudo pip3 install gatt pyyaml apscheduler qhue
sudo apt-get install python3-dbus
```

Make sure your Turn Touch is disconnected **and unpaired** from any other devices, then run:

```sudo gattctl --discover```

You should see the Turn Touch come up and see its MAC Address, which will look similar to `c2:51:f2:36:3f:ad`.

Put this mac address in config.yml, and update any button press options you would like to configure - just enter any bash script to run.

Launch the listener with:

```sudo python3 monitor.py```

It should connect, and once it has you should be able to press buttons on your Turn Touch and see the output of your commands.


## Hue Control

In order to connect to your Hue Bridge, it's easest to run:

```python3 hue.py```

This will prompt you to press the button on your bridge, then list out your lights, by id, type and room.
You can then configure button presses in `config.yml` as follows:

```north_double:
    type: hue
    id: 1 # From output of python3 hue.py
    brightness: # 1-254
    hue: 9000 # From 0 to 65535, hardware dependent
```

Setting scenes, or rooms is not possible, yet!
