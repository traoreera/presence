import paho.mqtt.client as paho
from paho import mqtt

from ..config import MQTTConfig
from ..crud import cards


class OPTIONS:
    CARD = cards.CardCruds()


class LocketCmd:

    # MQTT Commands locket
    OPEN: str = "0x001020"
    CLOSE: str = "0x003020"
    PUBLISH: str = "0x10806"
    RESET: str = "0x10807"
    STATUS: str = "0x10808"
    CMD: str = "/0x10809"

    def uq_user_topic_cmds(self, base: str, types: str, user_id: str):

        if types == "cmd":
            return f"{base}/{user_id}{self.CMD}"
        if types == "pub":
            return f"{base}/{user_id}"

    def msg_add(self, msg: str):
        return f"{self.CARDADD}{msg}"

    def removeCard(self, msg: str):
        return f"{self.CARDREMOVE}{msg}"


class MqttClient:

    def __init__(self):

        self.client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
        # calback
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # confiuration
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(MQTTConfig.USERNAME, MQTTConfig.PASSWORD)
        self.client.connect(MQTTConfig.BROKER_URL, MQTTConfig.BROKER_PORT)

        self.loop: bool = True

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(
            f"[{flags['session present']}]-> broker Locket [mqtt] connecte. status: {rc}"
        )
        client.subscribe("#", qos=2)

    def on_message(self, client, userdata, msg):
        content = msg.topic.split("/")
        if len(content) == 3:
            print(f"{content} => {msg.payload.decode()}")
            if content[-1] == "0x3306":
                if msg.payload.decode() == "online":
                    print("user online")
                print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
                # Handle the message as needed
                print(f"Message content: {msg.payload.decode()}")
                response = OPTIONS.CARD.get_user_acess(content[1], msg.payload.decode())
                if response:
                    self.publish(
                        MqCmd.uq_user_topic_cmds(content[0], "cmd", content[1]),
                        MqCmd.OPEN,
                    )
                else:
                    self.publish(
                        MqCmd.uq_user_topic_cmds(content[0], "cmd", content[1]),
                        MqCmd.CLOSE,
                    )
        else:
            print(f"{content} => {msg.payload.decode()}")

    def publish(self, topic: str, msg: str):
        self.client.publish(topic, msg)
        print(f"Published message to topic {topic}: {msg}")
        return

    def loopMqttServerListener(self):
        self.client.loop_start()

    def stop(self):
        self.loop = False
        self.client.loop_stop()
        self.client.disconnect()

    def status(
        self,
        topic: str,
        user_id: str,
    ):
        self.publish(MqCmd.uq_user_topic_cmds(topic, "cmd", user_id), MqCmd.STATUS)


try:
    clientMq = MqttClient()
except Exception as e:
    print(f"error detecting in mqtt {e}")
    clientMq = None
MqCmd = LocketCmd()
