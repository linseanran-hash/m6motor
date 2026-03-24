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

class MockIO:
    def __init__(self):
        print("[Mock] 模拟硬件 IO 已启动")

    def write(self, data):
        # 将发给电机的十六进制指令打印出来，而不是发往串口
        hex_data = ' '.join(['%02X' % b for b in data])
        print(f"[Mock -> Motor] 发送指令: {hex_data}")

    def read(self, length):
        # 模拟电机的返回（例如永远返回成功状态）
        return b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a' 

# 在 main.py 组装时切换
# io = get_io() 
io = MockIO()
# 单例导出
# io = MotorIO()