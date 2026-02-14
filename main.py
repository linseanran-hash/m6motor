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

    def get_other_feedback(self):
        """打印当前电机的状态信息"""
        # 构造 0x74 指令，DATA[6] 填入枚举对应的 value
        mode_data = bytearray([0]*7)
        packet = bytearray([self.motor_id, 0x74]) + mode_data
        packet.append(crc8_maxim(packet))
        
        self.ser.write(packet)
        res = self.ser.read(10)
        if len(res) == 10:
            # 根据手册解析反馈：DATA[2-3]电流，DATA[4-5]是速度，DATA[6]是温度，DATA[7]是角度
            # Data[8] 是错误码
            real_current = struct.unpack('>h', res[2:4])[0]
            real_speed = struct.unpack('>h', res[4:6])[0]
            temp = res[6]
            real_angle = res[7]
            fault_value = res[8]
            print(f"电机【{res[0]}】,运行mode:{hex(res[1])}, 转速: {real_speed} RPM 温度: {temp}℃ ,角度: {real_angle}, fault_value:{fault_value} 。")
        else:
            print(f"\r no response.")
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

    def move_to_angle(self, angle_deg:int):
        """
        直接设置角度 (0-360)
        """
        # 1. 角度映射：0~360 -> 0~32767
        target_val = int((angle_deg % 360) * (32767 / 360.0))
        
        # 2. 构造数据包 (根据截图1)
        # field[2-3]: 角度高低位
        # field[6]: Acceleration (建议给个 0x20 防止过冲)
        # field[7]: Brake (0x00)
        angle_bytes = struct.pack('>h', target_val) # UINT16 大端序
        control_data = angle_bytes + bytearray([0, 0, 0x01, 0x00, 0])
        
        packet = bytearray([self.motor_id, 0x64]) + control_data
        packet.append(crc8_maxim(packet))
        
        print(f"发送位置指令: {angle_deg}° (原始值: {target_val})")
        self.ser.write(packet)
        
        # 3. 读取反馈确认
        res = self.ser.read(10)
        if len(res) == 10:
            # 根据截图解析 DATA[6-7]
            current_angle_raw = struct.unpack('>h', res[6:8])[0]
            current_angle_deg = (current_angle_raw / 32767.0) * 360.0
            print(f"电机：{res[0]}, 反馈当前模式：{hex(res[1])}, 当前位置: {current_angle_deg:.2f}°")
        else:
            print(f"no response")

    def stop(self):
        print("\n>>> 电机停止并释放状态")
        stop_packet = bytearray([self.motor_id, 0x64]) + bytearray([0]*7)
        stop_packet.append(crc8_maxim(stop_packet))
        self.ser.write(stop_packet)

# =================使用示例=================
if __name__ == "__main__":
    winder = WinderController('COM8')
    try:
        winder.stop()
        time.sleep(0.05)
        winder.get_other_feedback()
        # 正转 3 秒
        # winder.run_speed(150, 3) 
        winder.set_mode(MotorMode.POSITION)
        time.sleep(0.05)
        winder.get_other_feedback()
        while True:
            target = input("输入目标角度 (0-360) 或 Q 退出: ")
            if target.upper() == 'Q': break
            winder.move_to_angle(int(target))
            time.sleep(0.05)
            winder.get_other_feedback()
        # 反转 2 秒（如果需要回线）
        # winder.run_speed(-100, 2)
    finally:
        winder.stop()