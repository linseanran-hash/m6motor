import sys

# 统一尝试导入配置
try:
    from . import config
except ImportError:
    # 提醒用户：在 PC 上这通常是必要的，在 ESP32 上可能已经固化在固件里
    config = None

class MotorIO:
    def __init__(self):
        if sys.platform == 'esp32':
            from machine import UART
            # 优先从 config 读取引脚，如果没有则使用默认 GPIO
            tx_pin = getattr(config, 'ESP32_TX', 17) if config else 17
            rx_pin = getattr(config, 'ESP32_RX', 16) if config else 16
            self.bus = UART(2, baudrate=115200, tx=tx_pin, rx=rx_pin)
            self.is_mcu = True
        else:
            self.bus = serial.Serial(port, 115200, timeout=0.1)
            import serial
            if not config or not hasattr(config, 'SERIAL_PORT'):
                print("\n[错误] PC 端必须在 modules/config.py 中定义 SERIAL_PORT")
                sys.exit(1)
            self.bus = serial.Serial(config.SERIAL_PORT, 115200, timeout=0.1)
            self.is_mcu = False

    def write(self, data):
        return self.bus.write(data)

    def read(self, n):
        return self.bus.read(n)

# 单例导出
io = MotorIO()