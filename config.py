from dotenv import load_dotenv

import deps

load_dotenv(dotenv_path="./plugins/presence/.env")


class MQTTConfig:
    BROKER_URL = deps.os.getenv("BROKER_URL")
    USERNAME = deps.os.getenv("USERNAME")
    PASSWORD = deps.os.getenv("PASSWORD")
    BROKER_PORT = 8883
