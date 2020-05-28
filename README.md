# hmkit-python-parking-meter

### Overview  ###

This sample app for python bluetooth shows the basic use of Python HMKit to authenticate with the car emulator, send and receive a command through bluetooth.
Parking Meter App to demonstrate Python SDK with Head unit-Notification capable cars.

### Where to find supporting documentations? ###

Developer Center:
https://developers.high-mobility.com/

Getting Started with Python Bluetooth Beta SDK:
https://high-mobility.com/learn/tutorials/sdk/python/

Code References:
https://high-mobility.com/learn/documentation/iot-sdk/python/hmkit/

### Configuration ###

Set Python 3.7 as default in alternatives.

Install python hmkit sdk in the "Raspberry Pi Zero W or Pi Model3 B or Pi Model3 B+" board from github repo:
https://github.com/highmobility/hmkit-python

Before running the parking meter app, make sure to configure the following in the app:
(Refer Getting Started: https://high-mobility.com/learn/tutorials/sdk/python/)
1. Initialise hmkit with a valid Device Certiticate from the Developer Center https://developers.high-mobility.com/
2. Find the Access Token in respective emulator from https://developers.high-mobility.com/ and paste it in the source code to download Access Certificates from the server.


### Run the app ###

Disable system default Bluetooth software elements (run once per reboot)
$./sys_bt_off.sh

Run the app on your raspberry board, to see the basic flow:

1. Initialising the SDK
2. Getting Access Certificates
3. Bluetooth Connecting and authenticating with an emulator
4. Sending and receiving commands

$./parking_meter_app.py
Raspberry Pi device need internet access to be able to download Access Certificate.

## Contributing

We would love to accept your patches and contributions to this project. Before getting to work, please first discuss the changes that you wish to make with us via [GitHub Issues](https://github.com/highmobility/hmkit-python-parking-meter/issues), [Spectrum](https://spectrum.chat/high-mobility/) or [Slack](https://slack.high-mobility.com/).

See more in [CONTRIBUTING.md](https://github.com/highmobility/hmkit-python-parking-meter/blob/master/CONTRIBUTING.md)

## License ##

This repository is using MIT license. See more in [LICENSE](https://github.com/highmobility/hmkit-python-parking-meter/blob/master/LICENSE)
