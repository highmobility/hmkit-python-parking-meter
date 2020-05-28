#!/usr/bin/env python
"""
The MIT License

Copyright (c) 2014- High-Mobility GmbH (https://high-mobility.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys
import codecs
import traceback
import datetime
import time
from hmkit import hmkit, linklistener, broadcastlistener, autoapi
import hmkit.autoapi as hm_autoapi
#from hmkit.autoapi import autoapi_dump
from hmkit.autoapi.command_resolver import CommandResolver
from hmkit.autoapi.commands import *
from hmkit.autoapi.commands.lockunlockdoors import LockUnlockDoors
from hmkit.autoapi.commands.notification import Notification
from hmkit.autoapi.commands import get_ignition_state, turn_ignition_onoff, get_vehiclestatus
from hmkit.autoapi.properties.value.lock import Lock
from hmkit.autoapi.properties.value.charging.charge_mode import ChargeMode
from hmkit.autoapi.properties.value.charging.charge_timer import ChargingTimer, TimerType
from hmkit.autoapi.properties.value.charging.charge_port_state import ChargePortState
from hmkit.autoapi.properties.value.charging.reduction_time import ReductionTime
from hmkit.autoapi.properties.value.action_item import ActionItem
from hmkit.autoapi.properties.value.start_stop import StartStop
from hmkit.autoapi.commands.setreduction_chargingcurrent_times import SetReductionChargingCurrentTimes
from hmkit.autoapi.properties.permission_location import PermissionLocation, PermissionType
from hmkit.autoapi.properties.permissions import Permissions
from hmkit.autoapi.properties.bit_location import BitLocation
from hmkit.autoapi.identifiers import Identifiers
from hmkit.autoapi import msg_type

import logging

log = logging.getLogger('hmkit')


class Link_Listener(hmkit.linklistener.LinkListener):

    def __init__(self, app_instance):
        self.app = app_instance

    def command_incoming(self, link, cmd):
        """
        Callback for incoming commands received from bluetooth link.
        Change in States will be received in this callback

        :param link Link: :class:`link` object
        :param bytearray cmd: data received
        :rtype: None
        """

        log.info("Len: " + str(len(cmd)))
        #log.debug("\n App: Cmd :", cmd)
        b_string = codecs.encode(cmd, 'hex')
        log.info("Hex:* " + str(b_string) + " + Type: " + str(type(b_string)))

        hmkit_inst = hmkit.get_instance()
        hmkit_inst.autoapi_dump.message_dump(cmd)

        cmd_obj = CommandResolver.resolve(cmd)
        log.debug("cmd_obj: " + str(cmd_obj))
        #log.debug(" isinstance of LockState: " + str(isinstance(cmd_obj, lockstate.LockState)))

        self.app.incoming_message(cmd_obj)

        return 1

    def command_response(self, link, cmd):
        """
        Callback for command response received from bluetooth link
        Usually Acknowledgements

        :param link Link: :class:`link` object
        :param bytearray cmd: data received
        :rtype: None
        """

        log.info(" Msg: " + str(cmd) + " Len: " + str(len(cmd)))
        #print("\n LinkListener: App, Response Msg :", cmd)
        #b_string = codecs.encode(cmd, 'hex')
        #print("Response Hex: ", b_string, ", Type: ", type(b_string))
        #hmkit_inst = hmkit.hmkit.get_instance()
        #hmkit_inst.autoapi_dump.message_dump(cmd)
        return 1


class Broadcast_Listener(hmkit.broadcastlistener.BroadcastListener):

    def __init__(self, app_instance):
        #print(" hm_app BroadcastListener(), __init__() ")
        self.bt_connected = 0;
        self.app = app_instance

    def connected(self, Link):
        log.info("App: Link connected")
        #print("App: Link connected")
        self.bt_connected = 1;

        # call the app
        self.app.car_connected()

        #return 1

    def disconnected(self, Link):
        log.info("App: Link disconnected")
        #print("App: Link disconnected")
        self.bt_connected = 0;
        return 1

    def state_changed(self, state, old_state):
        # code: place holder api
        log.info("state_changed")
        print("state_changed")

# -----------------------------------------------------------------------------
# =============== Parking Machine Logics =================
# -----------------------------------------------------------------------------

class ParkingMachine():

    def __init__(self, hmkit):
        print(" ParkingMachine, __init__() ")
        self.hmkit = hmkit
        self.connected_vehicles = {}
        # TODO: change it for multiple devices
        self.vin = None
        self.parking_intended = False

    def incoming_message(self, cmd_obj):
        print("ParkingMachine: incoming_message")
        # resolve the received message to instances
        # process it based on the message instances, drop all other messages
        if isinstance(cmd_obj, vehicle_status.VehicleStatus):
            self.process_vehicle_status(cmd_obj)
        elif isinstance(cmd_obj, notification_action.NotificationAction):
            print("notifications_state.NotificationAction")
        elif isinstance(cmd_obj, notifications_state.NotificationsState):
            print("notifications_state.NotificationsState")
            self.process_notifications_response(cmd_obj)
        elif isinstance(cmd_obj, ignition_state.IgnitionState):
            self.process_ignition_state_change(cmd_obj)
        elif isinstance(cmd_obj, parkingticket.ParkingTicket):
            print("ParkingTicket")
        else:
            print(" Received uninterested message hence dropping it: " + str(type(cmd_obj)))

    def car_connected(self):
        print("ParkingMachine: car_connected")
        # see if there is a Parked_Vehicle instance if not
        # create one, pass the event to the instance
        time.sleep(1)
        self.send_get_vehicle_status()

    def send_get_vehicle_status(self):
        print("ParkingMachine: send_get_vehicle_status")
        constructed_bytes = get_vehiclestatus.GetVehicleStatus().get_bytearray()
        # TODO, need to consider multiple link devices
        self.hmkit.bluetooth.link.sendcommand(constructed_bytes)

    def send_start_parking(self, parkedvehicle):
        print("ParkingMachine: send_start_parking")
        startdatetime = datetime.datetime.now()
        enddatetime = startdatetime + datetime.timedelta(days=1)
        constructed_bytes = start_parking.StartParking(None,"Berlin Parking","76543",startdatetime, enddatetime ).get_bytearray()
        self.hmkit.bluetooth.link.sendcommand(constructed_bytes)
        parkedvehicle.start_parking()

    def send_stop_parking(self, parkedvehicle):
        print("ParkingMachine: send_stop_parking")
        constructed_bytes = end_parking.EndParking().get_bytearray()
        self.hmkit.bluetooth.link.sendcommand(constructed_bytes)
        parkedvehicle.stop_parking()

    def send_start_parking_intend_notification(self, parkedvehicle):
        print("ParkingMachine: send_start_parking_intend_notification")
        #action_no = ActionItem(0, "No")
        action_yes = ActionItem(1, "Yes")
        actionitems = []
        #actionitems.append(action_no)
        actionitems.append(action_yes)
        constructed_bytes = Notification("Would you like to Park", actionitems).get_bytearray()
        self.hmkit.bluetooth.link.sendcommand(constructed_bytes)

    def send_stop_parking_intend_notification(self, parkedvehicle):
        print("ParkingMachine: send_stop_parking_intend_notification")
        #action_no = ActionItem(0, "No")
        action_yes = ActionItem(1, "Yes")
        actionitems = []
        #actionitems.append(action_no)
        actionitems.append(action_yes)
        constructed_bytes = Notification("Would you like to End Parking", actionitems).get_bytearray()
        self.hmkit.bluetooth.link.sendcommand(constructed_bytes)

    def process_notifications_response(self, cmd_obj):
        print("ParkingMachine: process_notifications_response")

        activated_action_id = cmd_obj.get_activated_action_id()
        if activated_action_id is None:
            print("ParkingMachine: notifications_state: action id is not activated")
            return

        parkedvehicle = self.connected_vehicles.get(self.vin)
        cur_parking_state = parkedvehicle.get_parking_state()

        log.info(" Activated Action ID: " + str(activated_action_id))

        if activated_action_id == 0: # NO Response
            # not going to park.
            # remove the instance from the dict list
            if cur_parking_state is True: # Already Being Parked, responsed for stop parking
                print("Vehice Num: " + str(self.vin) + " intends to continue park")
            else: # Not parked Already, response for start parking
                print("Vehice Num: " + str(self.vin) + " does not intend to park")

        elif activated_action_id == 1: # Yes Response

            if cur_parking_state is True: # Already Being Parked, response for stop parking
                print("Vehice Num: " + str(self.vin) + " intends to End park")
                self.send_stop_parking(parkedvehicle)
                self.parking_intended = False
            else:
                # Not parked Already but intends to park, listen for Ignition stop
                self.parking_intended = True
                ignition_state = self.veh_status.get_state_ignition()
                ignition = ignition_state.get_engine_ignition()
                print("Vehice Num: " + str(self.vin) + " intends to park. Ignition: " + str(ignition))
                # Vehicle Ignition is already OFF during the parking notification
                if ignition is False:
                    # send start parking
                    self.send_start_parking(parkedvehicle)
        else: # Not a expected value
                log.info(" Action ID does not match: " + str(activated_action_id))


    def process_vehicle_status(self, cmd_obj):

        print("ParkingMachine: process_vehicle_status")
        licenseplate = cmd_obj.get_licenseplate()
        # TODO: need to handle multiple vehicles vin.
        # cannot store in self of ParkingMachine
        self.vin = cmd_obj.get_vin()
        self.veh_status = cmd_obj

        parkedvehicle = None
        if self.vin not in self.connected_vehicles:
            parkedvehicle = Parked_Vehicle(self.vin, licenseplate)
            self.connected_vehicles[self.vin] = parkedvehicle
        else:
            parkedvehicle = self.connected_vehicles.get(self.vin)

        print("Vehice ID Num: " + str(self.vin) + " Licenseplate: " + str(licenseplate))
        # send notification
        self.send_start_parking_intend_notification(parkedvehicle)

    def process_ignition_state_change(self, cmd_obj):
        print("ParkingMachine: process_ignition_state_change")
        ignition = cmd_obj.get_engine_ignition()
        print("Ignition State Changed: " + str(ignition))
        # TODO: need to handle multiple vehicles vin.
        parkedvehicle = self.connected_vehicles.get(self.vin)
        cur_parking_state = parkedvehicle.get_parking_state()

        if self.parking_intended is not True:
            print("ParkingMachine: parking_intended is not True")
            # Process ignition state only for Parking intended Car
            return

        if ignition is True:
            if cur_parking_state is True: # Already Being Parked, Ignition ON
                print("Vehice Num: " + str(self.vin) + "Ignition ON when Parked")
                # send stop parking
                self.send_stop_parking_intend_notification(parkedvehicle)
            else:
                # Not parked Already, Nothing to do
                print("Vehice Num: " + str(self.vin) + "Ignition ON when Not Parked, nothing to do state")
        else:
            if cur_parking_state is True: # Already Being Parked, Ignition OFF
                print("Vehice Num: " + str(self.vin) + "Ignition OFF when Already Parked, nothing to do state")
                #self.send_stop_parking(parkedvehicle)
            else:
                # Not parked Already, Ignition OFF -> Start Parking
                print("Vehice Num: " + str(self.vin) + " Ignition OFF when not Parked")
                # send start parking
                self.send_start_parking(parkedvehicle)

# store the vehicle details
# store the parking start details
# store the parking stopped details
class Parked_Vehicle():

    def __init__(self, vin, license_plate):
        print(" Parked_Vehicle, __init__() ")
        self.parking_started = False
        self.vin = vin
        self.license_plate = license_plate        

    def start_parking(self):
        print(" Parked_Vehicle, start_parking() ")
        self.parking_started = True

    def stop_parking(self):
        print(" Parked_Vehicle, stop_parking() ")
        self.parking_started = False
    
    def get_parking_state(self):
        return self.parking_started

    def get_vin(self):
        print(" Parked_Vehicle, get_vin() ")
        return self.vin

    def get_licenseplate(self):
        print(" Parked_Vehicle, get_licenseplate() ")
        return self.license_plate


# -----------------------------------------------------------------------

if __name__== "__main__":

    # Initialise with HMKit class with a Device Certificate and private key. To start with
    # this can accept Base64 strings straight from the Developer Center


    hmkit = hmkit.HmKit(["<< COPY DEVICE CERTIFICATE HERE >>"], logging.INFO)

    # Download Access Certificate with the token
    try:
        hmkit.get_instance().download_access_certificate(b"<< COPY THE TOKEN HERE >>")
    except Exception as e:
        # Handle the error
        #log.critical("Error in Access certicate download " + str(e.args[0]))
        #hmkit.hmkit_exit()
        print("empty")

    parkingmachine = ParkingMachine(hmkit)

    # local LinkListener object of sampleapp
    linkListener = Link_Listener(parkingmachine)

    # local BroadcastListener object of sampleapp
    broadcastListener = Broadcast_Listener(parkingmachine)

    # set link listener for BLE link device events
    hmkit.bluetooth.link.set_listener(linkListener)

    # set Broadcast listener for BT broadcast events
    hmkit.bluetooth.broadcaster.set_listener(broadcastListener)

    # Start BLE broadcasting/advertising
    hmkit.bluetooth.startBroadcasting()

    #hmkit.bluetooth.stopBroadcasting()
