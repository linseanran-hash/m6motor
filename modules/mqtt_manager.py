import sys

class MQTTManager:
    def __init__(self, client_id, broker, port, callback):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.callback = callback
        self.client = None
        self._init_client()

    def _init_client(self):
        if sys.platform == 'esp32':
            from umqtt.simple import MQTTClient
            self.client = MQTTClient(self.client_id, self.broker, port=self.port)
            self.client.set_callback(self.callback)
        else:
            import paho.mqtt.client as mqtt
            # PC 端适配 paho-mqtt 接口
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, self.client_id)
            self.client.on_message = lambda c, u, m: self.callback(m.topic, m.payload)

    def connect(self, topics):
        if sys.platform == 'esp32':
            self.client.connect()
            # 兼容处理：如果是单个字符串转为列表
            if isinstance(topics, str): topics = [topics]
            for t in topics:
                self.client.subscribe(t)
        else:
            self.client.connect(self.broker, self.port)
            if isinstance(topics, str): topics = [topics]
            for t in topics:
                self.client.subscribe(t)
            self.client.loop_start() # PC 端开启后台循环

    def check_msg(self):
        """MicroPython 需要主动轮询消息"""
        if sys.platform == 'esp32':
            self.client.check_msg()

    def publish(self, topic, msg):
        self.client.publish(topic, str(msg))