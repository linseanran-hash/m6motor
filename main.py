import serial
import struct
import time
from enum import Enum

# 定义电机模式枚举
class MotorMode(Enum):
    CURRENT  = 0x01  # 电流模式
    VELOCITY = 0x02  # 速度模式
    POSITION = 0x03  # 位置模式

# crc 校验
def crc8_maxim(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ 0x8C
            else:
                crc >>= 1
    return crc

# 电机控制类
class WinderController:
    def __init__(self, port='COM7'):
        self.ser = serial.Serial(port, 115200, timeout=0.5)
        self.motor_id = 0x01

    def set_mode(self, mode: MotorMode):
        """
        使用枚举设置电机模式
        用法: winder.set_motor_mode(MotorMode.VELOCITY)
        """
        print(f"正在切换模式至: {mode.name} (代码: {hex(mode.value)})")
        
        # 构造 A0 指令，DATA[6] 填入枚举对应的 value
        mode_data = bytearray([0, 0, 0, 0, 0, 0, mode.value])
        packet = bytearray([self.motor_id, 0xA0]) + mode_data
        packet.append(crc8_maxim(packet))
        
        self.ser.write(packet)
        time.sleep(0.2)

    def run_speed(self, rpm, seconds):
        print(f">>> 启动卷线：{rpm} RPM，持续 {seconds} 秒")
        self.set_mode(MotorMode.VELOCITY) # 强制进入速度模式
        
        speed_hex = struct.pack('>h', rpm)
        # 构造 7 字节 DATA：速度(2字节) + 加速度/电流限制等(5字节)
        control_data = speed_hex + bytearray([0, 0, 0, 0, 0])
        
        start_time = time.time()
        try:
            while time.time() - start_time < seconds:
                packet = bytearray([self.motor_id, 0x64]) + control_data
                packet.append(crc8_maxim(packet))
                self.ser.write(packet)
                
                # 读取电机反馈
                res = self.ser.read(10)
                if len(res) == 10:
                    # 根据手册解析反馈：DATA[4-5]是速度，DATA[6]是温度
                    real_speed = struct.unpack('>h', res[4:6])[0]
                    temp = res[6]
                    print(f"\r[运行中] 实际转速: {real_speed} RPM | 电机温度: {temp}℃ ", end="")
                else:
                    print(f"\r no response.")
                
                time.sleep(0.05) # 20Hz 刷新，保证控制平滑
        except KeyboardInterrupt:
            print("\n[警告] 用户手动停止！")
        
        # 任务结束，停止电机
        self.stop()

    def stop(self):
        print("\n>>> 电机停止并释放状态")
        stop_packet = bytearray([self.motor_id, 0x64]) + bytearray([0]*7)
        stop_packet.append(crc8_maxim(stop_packet))
        self.ser.write(stop_packet)

# =================使用示例=================
if __name__ == "__main__":
    winder = WinderController('COM8')
    try:
        # 正转 3 秒
        winder.run_speed(150, 3) 
        time.sleep(1)
        # 反转 2 秒（如果需要回线）
        # winder.run_speed(-100, 2)
    finally:
        winder.stop()