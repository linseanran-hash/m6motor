# emulator.py
import paho.mqtt.client as mqtt
import json
import time

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "test_console")
client.connect("127.0.0.1", 1883)

commands = [
    {"dist": 10, "speed": 100},
    {"dist": -5, "speed": 200},
    {"stop": True}
]

for cmd in commands:
    topic = "winder/01/move" if "dist" in cmd else "winder/01/stop"
    client.publish(topic, json.dumps(cmd))
    print(f"已发送指令到 {topic}: {cmd}")
    time.sleep(2)