# tg-mirror
用 **MTProto**（api id / api hash）登录成一个“用户账号”（userbot），可以看到并操作群里其它机器人的消息——这在普通 **Bot API** 是绝对做不到的

1. **监听指定群**的新消息；

2. 发现 `sender.bot == True`（即消息作者是一台机器人）时：
   
   - 先把这个机器人*过去发过的消息*全部删除（或只删你想删除的条数 / 时间段）；
   
   - 再把当前这条消息转发回同一群组。

> 💡 只有具备“删除消息”权限的管理员账号才能删除别人（包括机器人）的消息；请务必把你的 userbot 设为群管理员并勾选“删除消息”权限。

---

## 1. 准备工作

```bash
# 仅供参考，你也可以直接在宿主机跑
mkdir tg-clean-forward && cd tg-clean-forward

# 建议创建专门的 venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip telethon
```

然后把下面代码保存为 `listener.py`：

```bash
from telethon import TelegramClient, events

api_id   = 1234567
api_hash = "abcd1234efgh5678ijkl9012mnop3456"
group    = -1001234567890   # 你的群 long‑id 或 @link

client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=group))
async def on_bot_message(event):
    sender = await event.get_sender()
    if not getattr(sender, "bot", False):
        return  # 只处理机器人发的消息

    # Step 1: 转发（或复制）到同一群
    await event.message.forward_to(event.chat_id)
    # 如果想去掉“Forwarded from …”标签，可改成：
    # await client.send_message(event.chat_id, event.raw_text, file=event.media)

    # Step 2: 删除这条原始消息
    await event.delete()  # 等同于 client.delete_messages(event.chat_id, event.id)

print(">> Listening...")
client.start()
client.run_until_disconnected()
```

### 创建 `systemd` 服务配置文件，实现后台运行

创建服务文件：

```bash
sudo vim /etc/systemd/system/tg-forward-bot.service
```

内容如下（请确保路径正确）：

```bash
[Unit]
Description=Telegram Forward & Delete Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/tg-clean-forward
ExecStart=/root/tg-clean-forward/venv/bin/python listener.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

```

保存并退出。 



### 启动并设置开机自启

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable tg-forward-bot
sudo systemctl start tg-forward-bot
sudo systemctl status tg-forward-bot
```

查看运行日志：

```bash
journalctl -fu tg-forward-bot
```

停止并关闭 systemd 服务

```bash
sudo systemctl stop tg-forward-bot      # 停止正在运行的服务
sudo systemctl disable tg-forward-bot   # 取消开机自动启动
```

- 重启服务：

```bash
sudo systemctl restart tg-forward-bot
```
