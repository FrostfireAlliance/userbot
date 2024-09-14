from telethon import TelegramClient, events
import asyncio
from telethon.errors import ChatAdminRequiredError, ChatWriteForbiddenError, ChannelPrivateError, ChannelInvalidError, FloodWaitError, RpcCallFailError

api_id = '20045757'
api_hash = '7d3ea0c0d4725498789bd51a9ee02421'
phone = '+380983082762'

client = TelegramClient('userbot', api_id, api_hash)

forward_message = None
send_interval = 0
stop_sending = asyncio.Event()
sending_active = False
user_id = None
target_chat_id = None

@client.on(events.NewMessage(outgoing=True))
async def handle_message(event):
    global forward_message, send_interval, stop_sending, sending_active, user_id, target_chat_id

    if event.sender_id == user_id:
        print(f"Received message from self: {event.text}")

        if event.text.startswith('.start'):
            await event.edit(
        '**👨‍💻 Команды:**\n'
        '`.start` **- Показать это меню.**\n'
        '`.send (время в минутах) (ссылка на сообщение)` **- начать пересылку сообщений.**\n'
        '`.stop` **- остановить пересылку сообщений.**\n\n'
        '**👨‍💻 Создатель: foxy437.t.me**'
            )

        elif event.text.startswith('.send '):
            if sending_active:
                await event.edit('Я не могу 2 задачи одновременно выполнять...')
                return

            try:
                args = event.text.split(maxsplit=2)
                if len(args) < 3:
                    raise ValueError('Тупой... Вот так надо: .send (время в минутах) (ссылка на сообщение)')

                send_interval = int(args[1]) * 60
                link = args[2]

                parts = link.split('/')
                if len(parts) < 2:
                    raise ValueError('Я не могу найти сообщения по этой ссылке....')

                chat_id = parts[-2]
                message_id = int(parts[-1])

                if chat_id.startswith('c'):
                    chat_id = int(chat_id[1:])
                else:
                    chat_id = int(chat_id)

                target_chat_id = event.chat_id
                forward_message = (chat_id, message_id)
                sending_active = True
                stop_sending.clear()
                await event.edit(f'Начинаю пересылать сообщения каждые {send_interval // 60} минут.')

                while not stop_sending.is_set():
                    if forward_message:
                        chat_id, message_id = forward_message
                        try:
                            await client.forward_messages(target_chat_id, message_id, chat_id)
                            print(f"Forwarded message {message_id} from chat {chat_id}")
                        except (ChatAdminRequiredError, ChatWriteForbiddenError):
                            await event.reply('У меня прав нету(')
                            stop_sending.set()
                        except (ChannelPrivateError, ChannelInvalidError):
                            await event.reply('...')
                            stop_sending.set()
                        except FloodWaitError as e:
                            await event.reply(f'Эээ блять мне лимит поставили(((')
                            stop_sending.set()
                        except RpcCallFailError as e:
                            await event.reply(f'Что-то не получается у меня....')
                            stop_sending.set()
                        except Exception as e:
                            print(f"Что-то не получается у меня....")
                            await event.reply(f'Что-то не получается у меня....')
                    
                    await asyncio.sleep(send_interval)

            except ValueError as e:
                await event.edit(f'Ошибка: {str(e)}')
            except Exception as e:
                await event.edit(f'Ошибка: {str(e)}')

        elif event.text.startswith('.stop'):
            if not sending_active:
                await event.edit('Ты даже не запускал меня.....')
                return
            stop_sending.set()
            sending_active = False
            await event.edit('Остановил.')

async def main():
    global user_id
    await client.start(phone)
    me = await client.get_me()
    user_id = me.id
    await client.send_message(user_id,
        '**👨‍💻 Команды:**\n'
        '`.start` **- Показать это меню.**\n'
        '`.send (время в минутах) (ссылка на сообщение)` **- начать пересылку сообщений.**\n'
        '`.stop` **- остановить пересылку сообщений.**\n\n'
        '**👨‍💻 Создатель: foxy437.t.me**'
    )
    await client.run_until_disconnected()

client.loop.run_until_complete(main())
