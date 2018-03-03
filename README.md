# Turn Touch Raspberry Pi Client

## Installation

This code was written and tested with a Raspberry Pi Zero W.

Assuming python3 and pip3 are installed, install the following *as root*. Do not use a virtualenv!

```
sudo pip3 install gatt pyyaml apscheduler
sudo apt-get install python3-dbus
```

Make sure your Turn Touch is disconnected *and unpaired* from any other devices, then run:

```sudo gattctl --discover```

You should see the Turn Touch come up and see its Mac Address, which will look similar to c2:51:f2:36:3f:ad.

Put this mac address in config.yml, and update any button press options you would like to configure - just enter any bash script to run.

Launch the listener with:

```sudo python3 montior.py```

It should connect, and once it has you should be able to press buttons on your Turn Touch and see the output of your commands.
