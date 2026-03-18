# main.py
import time
from modules.hardware import io
from modules.m6_proto import M6Winder, MotorMode
import modules.config as config

def main():
    # 初始化卷线器控制逻辑
    winder = M6Winder(
        io_adapter=io, 
        motor_id=config.MOTOR_ID, 
        radius_cm=config.WINDER_RADIUS_CM
    )

    try:
        print("--- M6 电机控制系统启动 ---")
        winder.stop()
        time.sleep(1)
        
        # 演示：收线 18cm
        winder.move_distance(18, 100)
        time.sleep(1)
        
        # 演示：放线 18cm
        winder.move_distance(-18, 100)

    except KeyboardInterrupt:
        print("\n用户中断运行")
    finally:
        winder.stop()
        print("程序退出")

if __name__ == "__main__":
    main()