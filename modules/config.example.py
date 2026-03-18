# modules/config.example.py
# 这是一个配置模板文件。
# 请将其复制并重命名为 config.py，然后根据你的实际情况修改内容。

import sys

# --- 1. 串口配置 (根据系统取消注释或修改) ---
if sys.platform == 'win32':
    # Windows 示例：通常是 COMx
    SERIAL_PORT = 'COM7' 
elif sys.platform == 'darwin':
    # macOS 示例：通常是 /dev/cu.usbserial-xxx
    SERIAL_PORT = '/dev/cu.usbserial-110'
elif sys.platform.startswith('linux'):
    # Linux 示例：通常是 /dev/ttyUSB0 或 /dev/ttyACM0
    # 注意：Linux 用户需执行 `sudo usermod -a -G dialout $USER` 以获取权限
    SERIAL_PORT = '/dev/ttyUSB0'
else:
    # ESP32 专有引脚配置 (MicroPython 环境)
    # 在 ESP32 上，硬件层会自动识别 sys.platform == 'esp32'
    ESP32_TX = 17
    ESP32_RX = 16

# --- 2. 电机业务参数 (PC 与 ESP32 通用) ---
MOTOR_ID = 0x01
WINDER_RADIUS_CM = 3.0  # 卷线轴半径

# --- 3. 网络与 MQTT 配置 (主要用于 ESP32) ---
WIFI_SSID = "Your_WiFi_Name"
WIFI_PASS = "Your_WiFi_Password"

# MQTT Broker 地址：
# PC 本地调测可用 "localhost"
# ESP32 必须填真实的局域网 IP (例如 "192.168.1.100")
MQTT_BROKER = "localhost" 
MQTT_PORT = 1883