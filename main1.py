import serial
import struct
import time

# --- 1. 核心校验算法 (CRC-8/MAXIM) ---
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

# --- 2. 串口初始化 (请根据你的设备管理器修改 COM 号) ---
try:
    ser = serial.Serial('COM8', 115200, timeout=0.1)
    print("串口已连接")
except Exception as e:
    print(f"串口打开失败: {e}")
    exit()

def send_motor_cmd(motor_id, speed):
    """
    发送速度指令
    speed: 目标转速 (RPM)
    """
    # 构造控制指令 (0x64)
    # DATA[2-3] 为转速，DATA[7] 为刹车位 (0xFF为刹车，0x00为正常)
    speed_bytes = struct.pack('>h', speed)
    brake_byte = 0xFF if speed == 0 else 0x00
    
    data_body = speed_bytes + bytearray([0x00, 0x00, 0x00, brake_byte, 0x00])
    packet = bytearray([motor_id, 0x64]) + data_body
    packet.append(crc8_maxim(packet))
    
    ser.write(packet)

def main():
    motor_id = 0x01

    try:
        # 第一步：切换到速度模式 (0x02)
        print("切换至速度模式...")
        mode_data = bytearray([0, 0, 0, 0, 0, 0, 0x02])
        packet_mode = bytearray([motor_id, 0xA0]) + mode_data
        packet_mode.append(crc8_maxim(packet_mode))
        ser.write(packet_mode)
        time.sleep(0.1)

        # 第二步：启动电机 (设定转速 100 RPM)
        print("电机启动，计时 3 秒...")
        send_motor_cmd(motor_id, 100)
        
        # 核心逻辑：在这里让程序“睡” 3 秒
        time.sleep(3)

        # 第三步：停止电机
        print("时间到，电机停止。")
        send_motor_cmd(motor_id, 0)

    except KeyboardInterrupt:
        # 如果中途按 Ctrl+C，也要确保电机停止
        print("\n强制停止")
        send_motor_cmd(motor_id, 0)
    finally:
        ser.close()

if __name__ == "__main__":
    main()