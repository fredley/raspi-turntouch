# Turn Touch Raspberry Pi Client

An extendible client for using a [Turn Touch](https://shop.turntouch.com/) with a Raspberry Pi. Comes with Hue, Nest and custom script support out of the box.

## Installation

This code was written and tested with a Raspberry Pi Zero W.

Assuming python3 and pip3 are installed, install the following **as root**. Do not use a virtualenv!

```bash
sudo pip3 install -r requirements.txt
```

Make sure your Turn Touch is disconnected **and unpaired** from any other devices, then run:

```sudo gattctl --discover```

You should see the Turn Touch come up and see its MAC Address, which will look similar to `c2:51:f2:36:3f:ad`.

Put this mac address in config.yml, and update any button press options you would like to configure - just enter any bash script to run.

Launch the listener with:

```sudo python3 monitor.py```

It should connect, and once it has you should be able to press buttons on your Turn Touch and see the output of your commands.


## Controllers

To see what controllers are available, run

```sudo python3 monitor.py -l```

To see help for setting up commands for a controller, run, e.g.

```sudo python3 monitor.py -c hue```

and then to set them up, run, e.g.

```sudo python3 monitor.py -s hue```

Most controllers that connect to a device will need some kind of setup. Controllers will often print out helpful information (such as available bulbs, thermostats) after setup.

## Battery Status

The battery status is checked every hour. If you would like something to happen when it falls below a certain value, use the following:

```yaml
battery_10: # will trigger when battery level falls to 10%
    type: bash
    command: email_me.sh
```

## Running on boot

You probably want `raspi-turntouch` to run on boot. To do this, make sure the paths in `turntouch.service` are correct, then:

```bash
sudo cp turntouch.service /lib/systemd/system/turntouch.service
sudo systemctl daemon-reload
sudo systemctl start turntouch
sudo systemctl enable turntouch
```

You can see log output at `/var/log/turntouch.log`.

Make sure you have set up credentials for services such as Nest and Hue before doing this!

## Writing your own controller

* Decide on a name for your controller. In this example it is `custom`. This key must be used in the filename and `config.yml` entries.
* Create `controllers/custom_controller.py`
* Create a class called, e.b. `CustomController`. It *must* inherit from `BaseController`.
* Implement `perform(self, action)`, where action is a dict as passed from `config.yml`, and `init` for setup.
* In `config.yml`, simply address your controller as follows:

```yaml
north_press:
    type: custom
    arg1: Whatever you want
    another_arg:
        - can
        - even
        - be
        - a
        - list
```

If your controller is used for a common action, service or product, consider submitting a pull request!
