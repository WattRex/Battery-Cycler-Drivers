#!/usr/bin/python3
'''
Create a driver mqqtt broker to subsc.
'''
#######################        MANDATORY IMPORTS         #######################
from __future__ import annotations

#######################         GENERIC IMPORTS          #######################
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
    """Handle error communicating with DRvQTT broker .

    Args:
        Exception ([type]): [description]
    """
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
        """
        Callback function for successful connection to the broker.
        """
        if rc == 0:
            log.debug(f'Connected correctly to the broker. Flags: {flags}')
        else:
            log.critical(f'Connection failed. Returned code: {rc}, flags: {flags}')

    # Message receiving callback
    def on_message(self, client, userdata, msg : MQTTMessage): #pylint: disable=unused-argument
        """Handle a message received from the client .

        Args:
            client ([type]): [description]
            userdata ([type]): [description]
            msg (MQTTMessage): [description]
        """
        if msg.topic in self.__subs_topics:
            call_name = self.__subs_topics[msg.topic]
            call_name(msg.payload)
        else:
            log.error(f"Unknown message received from [{msg.topic}]. Complete message data: {msg}")
            self.__err_callback(msg.topic, msg.payload)

    def publish(self, topic, data):
        """Publish a message to a RabbitMQ topic

        Args:
            topic ([type]): [description]
            data ([type]): [description]
        """
        log.debug(f"Publishing to [{topic}]: {data}")
        prop = Properties(PacketTypes.PUBLISH)
        self.__client.publish(topic= topic, payload=data, qos=DRV_MQTT_QOS, properties=prop)

    def subscribe(self, topic, callback):
        """Subscribe to a topic

        Args:
            topic ([type]): [description]
            callback (function): [description]
        """
        log.debug(f"Subscribing to [{topic}]")
        self.__subs_topics[topic] = callback
        self.__client.subscribe(topic=topic, qos=DRV_MQTT_QOS)

    def process_data(self):
        """Processes the incoming data and waits for it to complete .
        """
        self.__client.loop(timeout=0.5)

    def close(self) -> None:
        """Disconnects the underlying client .
        """
        self.__client.disconnect()
