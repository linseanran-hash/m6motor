# M6 Motor Control System (MQTT Edition)

基于 Python/MicroPython 的 M6 串行总线电机控制系统。本项目采用模块化设计，支持在 PC (Windows/macOS/Linux) 和 ESP32 硬件上运行同一套核心逻辑。

## 1. 项目架构

项目采用**依赖注入**模式，确保业务逻辑与底层硬件、配置完全解耦。

* `main.py`: 项目入口，负责组装模块并处理业务流程。
* `modules/m6_proto.py`: 电机协议封装（纯逻辑，不依赖硬件）。
* `modules/mqtt_manager.py`: MQTT 通讯管理（自动适配 PC 和 ESP32）。
* `modules/hardware.py`: 硬件抽象层（HAL），处理串口驱动。
* `modules/config.py`: 个人本地配置文件（被 Git 忽略）。

## 2. 快速开始

### 2.1 环境准备
1.  **PC 端**：安装 Python 3.8+，执行 `pip install -r requirements.txt`。
2.  **ESP32 端**：确保已刷入 MicroPython 固件，并安装 `Pymakr` (VS Code 插件)。
3.  **MQTT Broker**：推荐使用 Docker 运行 Mosquitto。
    ```bash
    # 启动 Mosquitto
    docker compose up -d
    # 停止 mosquitto
    docker compose down
    ```

### 2.2 配置初始化
1.  进入 `modules/` 目录。
2.  将 `config.example.py` 复制并重命名为 `config.py`。
3.  **关键配置项说明**：
    * `MOTOR_ID`: 电机的硬件 ID。
    * `SERIAL_PORT`: PC 连接电机的串口号（Linux 用户请确保已加入 `dialout` 组）。
    * `MQTT_BROKER`: **重点**！ESP32 连接时必须填电脑的局域网 IP，不可填 `localhost`。


## 3. MQTT 控制协议

系统启动后将自动订阅以下主题（以 ID=01 为例）：

| Topic | 功能 | Payload 示例 |
| :--- | :--- | :--- |
| `winder/01/move` | 控制电机转动 | `{"dist": 10.5, "speed": 150}` |
| `winder/01/stop` | 紧急停止 | (任意内容) |


## 4. 开发规范

1.  **禁止硬编码**：不要在 `modules/` 下的类中直接 `import config`。所有配置项应通过构造函数 `__init__` 传入。
2.  **跨平台兼容**：编写代码时注意 `bytes` 和 `str` 的转换（尤其在处理 MQTT Topic 时）。
3.  **分支管理**：
    * `master`: 稳定版本。
    * `refactor`: 架构重构分支。
    * `mqtt`: 当前开发的网络功能分支。


## 5. 故障排查 (Troubleshooting)

* **ESP32 连不上 MQTT**：检查防火墙是否放行了 1883 端口；检查 `config.py` 是否使用了局域网 IP。
* **电机无响应**：检查 RS485 转接头接线 (A/B 是否接反)；检查 `MOTOR_ID` 是否匹配。
* **权限错误 (Linux)**：执行 `sudo usermod -a -G dialout $USER` 并重启。

## 6. 路线图 (Roadmap)
- [x] 模块化重构与依赖注入架构
- [x] 跨平台 MQTT 通讯管理
- [x] Docker 容器化 Broker 部署
- [ ] **异步 `uasyncio` 改造**：解决电机运动期间无法响应停止指令的阻塞问题。
- [ ] **阻力反馈监控**：通过电流反馈实现自动堵转保护。