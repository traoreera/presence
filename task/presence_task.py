import time

from plugins.presence.run import OPTIONS

metadata = {
    "title": "presence mqtt",
    "description": """
        This service listens to MQTT messages related to
        presence operations and processes them accordingly.
        The service will listen to MQTT messages related
        to presence operations and processes them accordingly.
        It will listen to MQTT messages related to presence
        operations and processes them accordingly.
    """,
    "version": "1.0.0",
    "author": "Tanga Group",
    "type": "service",
    "module": "plugins",
    "moduleDir": "plugins/presence",
    "status": True,
    "dependencies": ["mqtt"],
    "license": "MIT",
    "tags": ["mqtt", "service", "plugins"],
    "icon": "mdi:message-text",
    "homepage": "app/presence",
    "documentation": "http://app.tangagroup.com/docs/presence",
    "repository": "http://app.tangagroup.com/repo/presence",
    "issues": "http://app.tangagroup.com/issues/presence",
    "changelog": "http://app.tangagroup.com/changelog/presence",
    "support": "http://app.tangagroup.com/support/presence",
    "contact": {
        "email": "contact@tangagroup.com",
        "website": "http://app.tangagroup.com",
        "phone": "+1234567890",
    },
    "keywords": ["mqtt", "presence", "service", "plugins"],
    "created_at": "2023-10-01T00:00:00Z",
    "updated_at": "2023-10-01T00:00:00Z",
    "license_url": "http://app.tangagroup.com/license",
}


def service_main(service):
    print("Service mqtt Presence demarrer")
    while service.running:
        try:
            OPTIONS.clientMq.loopMqttServerListener()
        except Exception as e:
            print(f"Error in MQTT loop: {e}")
        time.sleep(1)  # Sleep to prevent tight loop in case of errors
    print("Service mqtt Presence arreter")
    OPTIONS.clientMq.stop()
    print("MQTT client disconnected")
    return True
