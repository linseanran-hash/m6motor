import struct
import time
import math
from enum import Enum

class MotorMode(Enum):
    CURRENT  = 0x01
    VELOCITY = 0x02
    POSITION = 0x03

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

class M6Winder:
    def __init__(self, io_adapter, motor_id=0x01, radius_cm=3.0):
        self.io = io_adapter  # 传入的是 hardware.py 里的 io 实例
        self.motor_id = motor_id
        self.radius = radius_cm

    def _send_packet(self, cmd, data_bytes):
        packet = bytearray([self.motor_id, cmd]) + data_bytes
        packet.append(crc8_maxim(packet))
        self.io.write(packet) # 统一调用接口

    def set_mode(self, mode: MotorMode):
        print(f"切换模式: {mode.name}")
        # 模式切换报文逻辑
        mode_data = bytearray([0, 0, 0, 0, 0, 0, 0, mode.value])
        self._send_packet(0xA0, mode_data)
        time.sleep(0.2)

    def run_speed_raw(self, rpm):
        """发送单次速度指令"""
        speed_hex = struct.pack('>h', rpm)
        control_data = speed_hex + bytearray([0, 0, 0, 0, 0])
        self._send_packet(0x64, control_data)

    def move_distance(self, distance_cm, speed_rpm=150):
        """卷线长度逻辑：PC和ESP32通用"""
        circumference = 2 * math.pi * self.radius
        circles = distance_cm / circumference
        duration = abs(circles) / (speed_rpm / 60)
        
        direction_speed = speed_rpm if distance_cm > 0 else -speed_rpm
        
        print(f"执行动作: {distance_cm}cm, 预计耗时: {duration:.2f}s")
        
        start_time = time.time()
        self.set_mode(MotorMode.VELOCITY)
        
        while time.time() - start_time < duration:
            self.run_speed_raw(direction_speed)
            # 尝试读取反馈（非阻塞）
            res = self.io.read(10)
            if len(res) == 10:
                real_speed = struct.unpack('>h', res[4:6])[0]
                print(f"\r当前转速: {real_speed} RPM", end="")
            time.sleep(0.05)
        
        self.stop()

    def stop(self):
        self._send_packet(0x64, bytearray([0]*7))