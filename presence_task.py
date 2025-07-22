import time

from plugins.presence.run import clientMq

metadata = {
    "title": "locket mqtt",
    "description": """
        This service listens to MQTT messages related to
        locket operations and processes them accordingly.
        The service will listen to MQTT messages related
        to locket operations and processes them accordingly.
        It will listen to MQTT messages related to locket
        operations and processes them accordingly.
    """,
    "version": "V1.0.0",
    "author": "Tanga Group",
}


def service_main(service):
    print("Service mqtt feelback demarrer")
    while service.running:
        try:
            time.sleep(1)
            clientMq.loopMqttServerListener()
        except Exception as e:
            print(f"error as found {e}")
            print("existing brocker servise ...")
            service.running = False
    clientMq.stop()
    print("Service mqtt feelback arret")
