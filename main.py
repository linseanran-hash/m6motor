# main.py
import time
import sys
# 跨平台 JSON 兼容处理
if sys.platform == 'esp32':
    import ujson as json
else:
    import json
from modules.hardware import io
from modules.m6_proto import M6Winder
import modules.config as config
from modules.mqtt_manager import MQTTManager

# 初始化电机逻辑
winder = M6Winder(io, motor_id=config.MOTOR_ID, radius_cm=config.WINDER_RADIUS_CM)

def handle_move(payload):
    """MQTT Move消息处理函数"""
    try:
        data = json.loads(payload)
        dist = data.get("dist", 0)   # 距离 (cm)
        speed = data.get("speed", 100) # 速度 (RPM)
        
        if dist != 0:
            print(f"\n[MQTT] 收到指令: 移动 {dist}cm, 速度 {speed}")
            winder.move_distance(dist, speed)
    except Exception as e:
        print(f"解析 MQTT 消息失败: {e}")

def on_message_received(topic, payload):
    # 统一转换 bytes 为 str
    if isinstance(topic, bytes):
        topic = topic.decode('utf-8')

    print(f"[MQTT] 收到消息: {topic}")

    # 使用 config 中定义的变量进行比对，完全避免硬编码字符串
    if topic == config.TOPIC_MOVE:
        handle_move(payload)
    elif topic == config.TOPIC_STOP:
        print("!!! 紧急停止指令 !!!")
        winder.stop()
    else:
        print(f"Not subcribe such topic:[{topic}]")
    

def main():
    # 初始化 MQTT
    mqtt = MQTTManager(config.MQTT_CLIENT_ID, config.MQTT_BROKER, config.MQTT_PORT, on_message_received)
    
    try:
        print("--- M6 电机控制系统启动 ---")
        winder.stop()
        time.sleep(1)
        
        print("正在连接 MQTT Broker...")
        mqtt.connect()
        print("系统就绪，等待 Topic:", config.TOPIC_CONTROL)
        
        while True:
            # 对于 MicroPython，需要不断检查是否有新消息
            mqtt.check_msg()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n用户中断运行")
    finally:
        winder.stop()
        print("程序退出")

if __name__ == "__main__":
    main()