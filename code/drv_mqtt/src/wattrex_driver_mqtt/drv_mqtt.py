#!/usr/bin/python3
'''
Create a base class used to register devices status.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations
import sys
import os
#######################         GENERIC IMPORTS          #######################
from enum import Enum
from time import sleep
#######################       THIRD PARTY IMPORTS        #######################
from paho.mqtt.client import Client, MQTTv311, MQTTMessage
from paho.mqtt.properties import Properties
from paho.mqtt.packettypes import PacketTypes

#######################    SYSTEM ABSTRACTION IMPORTS    #######################
from system_config_tool import sys_conf_read_config_params
from system_logger_tool import Logger, sys_log_logger_get_module_logger
log: Logger = sys_log_logger_get_module_logger(__name__)

#######################          PROJECT IMPORTS         #######################


#######################          MODULE IMPORTS          #######################

#######################              ENUMS               #######################

#######################             CLASSES              #######################
class DrvMqttBrokerErrorC(Exception):
    def __init__(self, msg):
        self.msg = msg


    def __str__(self):
        return self.msg

DRV_MQTT_QOS = 1

class DrvMqttDriverC:
    '''
    Configures the mqtt driver.
    '''
    def __init__(self, error_callback, cred_path : str) -> None:
        #Connection success callback
        cred = sys_conf_read_config_params(filename=cred_path, section='mqtt')
        self.__client = Client(protocol=MQTTv311, transport="tcp", reconnect_on_failure=True)
        self.__client.username_pw_set(cred['user'], cred['password'])
        self.__client.enable_logger(log)

        # Specify callback function
        self.__client.on_connect = self.on_connect
        self.__client.on_message = self.on_message
        self.__err_callback = error_callback

        # Establish a connection
        self.__client.connect(host=cred['host'], port=int(cred['port']), keepalive=80)
        n_attempts = 0
        self.__client.loop(timeout=0.5)
        while not self.__client.is_connected():
            self.__client.reconnect_delay_set(min_delay=0.5, max_delay=30)
            self.__client.loop(timeout=0.5)
            if n_attempts > 10:
                raise DrvMqttBrokerErrorC('Error connecting to mqtt broker')
            n_attempts += 1

        self.__subs_topics = {}

    def on_connect(self, client, userdata, flags, rc): #pylint: disable=unused-argument
        if rc == 0:
            log.debug(f'Connected correctly to the broker. Flags: {flags}')
        else:
            log.critical(f'Connection failed. Returned code: {rc}, flags: {flags}')

    # Message receiving callback
    def on_message(self, client, userdata, msg : MQTTMessage): #pylint: disable=unused-argument
        if msg.topic in self.__subs_topics:
            call_name = self.__subs_topics[msg.topic]
            call_name(msg.payload)
        else:
            log.error(f"Unknown message received from [{msg.topic}]. Complete message data: {msg}")
            self.__err_callback(msg.topic, msg.payload)

    def publish(self, topic, data):
        log.debug(f"Publishing to [{topic}]: {data}")
        prop = Properties(PacketTypes.PUBLISH)
        self.__client.publish(topic= topic, payload=data, qos=DRV_MQTT_QOS, properties=prop)

    def subscribe(self, topic, callback):
        log.debug(f"Subscribing to [{topic}]")
        self.__subs_topics[topic] = callback
        self.__client.subscribe(topic=topic, qos=DRV_MQTT_QOS)

    def processData(self):
        self.__client.loop(timeout=0.5)

    def close(self) -> None:
        self.__client.disconnect()

#######################            FUNCTIONS             #######################
def error(data):
    log.critical(f"Error callback: {data}")

def mode(data):
    log.error(f"Mode callback: {data}")

def refs(data):
    log.critical(f"Refs callback: {data}")

def main():
    global driver
    driver = DrvMqttDriverC(error)
    pwr_ref = 'ctrl/pwr_ref'
    mode_topic = 'ctrl/mode'
    driver.susbcribe(mode_topic, mode)
    driver.susbcribe(pwr_ref, refs)
    driver.publish(mode_topic, 'NORMAL')

    iter = -1
    while iter < 100:
        print(' [*] Waiting for messages. To exit press CTRL+C')
        driver.publish(pwr_ref, str(iter))
        driver.processData()
        sleep(1)
        iter+=1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Keyboard Interrupted')
        driver.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
