# M6 Motor Control System

基于 Python/MicroPython 的 M6 串行总线电机控制系统。支持卷线长度计算、速度控制与位置控制。

## 1. 硬件连接
* 电机：M6 串行总线电机
* 控制端：PC (USB 转 RS485) 或 ESP32
* 波特率：115200

## 2. 快速开始 (PC 端)
1. 克隆项目后，进入 `modules/` 目录。
2. 复制模板：`cp config.example.py config.py` (macOS/Linux) 或手工复制重命名 (Windows)。
3. 根据你的硬件连接情况，编辑 `config.py` 中的 `SERIAL_PORT`。
4. 安装依赖：`pip install -r requirements.txt`
5. 运行主程序：`python main.py`

## 3. 开发规范
* **环境管理**：建议使用 Conda 或 venv。
* **跨平台方案**：串口层通过 `modules/hardware.py` 自动适配。
* **硬件迁移**：代码设计兼顾 MicroPython 语法，核心逻辑位于 `modules/`。