# sub
# 监控所有电机状态
docker exec -it m6-mosquitto mosquitto_sub -h localhost -t "winder/+/status/" -v

# 向 ID 为 1 的电机发送位置指令
docker exec -it m6-mosquitto mosquitto_pub -h localhost -t "winder/01/move" -m '{"dist": 10, "speed": 100}'