# Minecraft-QQ-ChatBridge
Chat across multiple Minecraft servers and QQ groups with No Server configuration required.

## 快速开始

### 安装python和tmux

- `sudo apt install python tmux pip -y`

### 安装python依赖

- `pip install -r requirements.txt`
- `python main.py`

## 功能

<details>
  <summary>已开发</summary>

- [x] 和MCC通信，并获取到文本消息
- [x] 区分为聊天信息、阵亡信息、成就信息
- [x] 将消息转发到qq群
- [x] 将消息在服务器间互通
- [x] 从qq群转发信息到MCC，处理特殊信息
- [x] 与ChatImage mod联动以显示表情
- [x] 自动配置开启mcc，并允许附加到mcc上
- [x] 实现多服务器、多qq群支持
- [x] 实现命令交互控制

</details>

<details>
  <summary>挖坑</summary>

- [ ] 允许自定义开关和设定消息类型的频率
- [ ] 实现管理员私聊发送信息操作chatbridge
- [ ] 实现仪表盘

</details>

## 配置文件

配置文件存储在 `/asset/config.json`

### 聊天组
一个群号+多个服务器表示一个聊天组。

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