# Minecraft-QQ-ChatBridge
Chat across multiple Minecraft servers and QQ groups with No Server configuration required.

## Quick Start
- `pip install -r requirements.txt`
- `python main.py`

## Check List
- [x] 和MCC通信，并获取到文本消息
- [x] 区分为聊天信息、阵亡信息、成就信息
- [x] 将消息转发到qq群
- [x] 将消息在服务器间互通
- [ ] 并允许自定义开关和设定消息类型的频率
- [x] 从qq群转发信息到MCC，处理特殊信息
- [x] 与ChatImage mod联动以显示表情
- [x] 自动配置开启mcc，并允许附加到mcc上
- [x] 实现多服务器、多qq群支持
- [ ] 实现管理员私聊发送信息操作chatbridge
- [x] 实现命令交互控制

## Configuration Help

### Groups
一个群号+多个服务器表示一个聊天频道。

注意：一个服务器只能对应一个群号，比如下面的例子是**不合法**的

```json
"12333": ["server1", "server2"],
"45666": ["server1"]
```

正确的例子如下：

```json
"12333": ["server1", "server2"],
"45666": ["server3", "server4"]
```