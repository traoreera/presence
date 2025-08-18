import json
import time

from plugins.presence.run import OPTIONS


def service_main(service):
    print("Service mqtt presence demarrer")
    while service.running:
        try:
            OPTIONS.clientMq.loopMqttServerListener()
        except Exception as e:
            print(f"Error in presence MQTT loop: {e}")
        time.sleep(1)  # Sleep to prevent tight loop in case of errors
    print("Service mqtt presence arreter")
    OPTIONS.clientMq.stop()
    print("MQTT client disconnected")
    return True


def new_feedback_remove():
    print("new_feelback_remove")


with open("./plugins/presence/config.json") as f:
    config = json.load(f)
    metadata = config
try:
    metadata["con"] = [
        {
            "func": new_feedback_remove,
            "name": "feedback label changing by contab ",
            "misfire_grace_time": 100,
            "interval": "cron",
            "minutes": 2,
            "activate": True,
            "cron_params": {"day": "*", "month": "*", "hour": "0", "minute": "0"},
        },
    ]
except Exception as e:
    print(e)
