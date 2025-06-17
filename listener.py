import os, logging, asyncio
from telethon import TelegramClient, events

API_ID   = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
GROUP_ID = int(os.getenv("GROUP_ID"))          # 负数，如 -1001234567890

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(message)s")
client = TelegramClient("mirror_session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=GROUP_ID))
async def mirror_and_delete(event):
    if event.out or not event.sender.bot:      # 跳过自己发的，只处理 Bot
        return

    msg = event.message
    # === 1. 复制回群（不带“转发自”标记） ===
    if msg.media:
        await client.copy_messages(GROUP_ID, msg)   # 复制媒体/文件
    else:
        await client.send_message(GROUP_ID, msg.text or "")

    # === 2. 删除原 Bot 消息 ===
    await client.delete_messages(GROUP_ID, msg.id)
    logging.info("已复制并删除 Bot 消息 %s", msg.id)

client.start()                 # 首次运行会要求手机号+验证码
client.run_until_disconnected()
