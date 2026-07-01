import asyncio
from telethon import TelegramClient, connection, events, types, errors

from app.settings import settings
from app.bot.llm import predictor
from app.bot.constants import default_welcome, default_answer
from app.bot.utils import get_language_code


bot = TelegramClient('bot_session',
                     api_id=settings.API_ID,
                     api_hash=settings.API_HASH,
                     connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                     proxy=(settings.PROXY_HOST, settings.PROXY_PORT, settings.PROXY_SECRET))


@bot.on(events.NewMessage(func=lambda e: e.is_private or e.is_group, pattern=r'^/start$'))
async def go_start(event):
    sender = await event.get_sender()
    if isinstance(sender, types.User): # type: ignore
        language_code = get_language_code(getattr(sender, 'lang_code', 'ru'))
        welcome_text = await predictor.translate(language_code, default_welcome)
        await event.respond(welcome_text)
    raise events.StopPropagation


@bot.on(events.NewMessage(func=lambda e: e.is_private or e.is_group, pattern=r'^/predict$'))
async def go_predict(event):
    sender = await event.get_sender()
    if isinstance(sender, types.User): # type: ignore
        language_code = get_language_code(getattr(sender, 'lang_code', 'ru'))
        full_prediction = ''
        prediction = await event.reply('...')

        async for chunk in predictor.generate_prediction(language_code):
            full_prediction += chunk
            await asyncio.sleep(0.3)
            try:
                await bot.edit_message(event.chat_id, prediction.id, full_prediction + ' ...', parse_mode='markdown')
            except errors.MessageNotModifiedError:
                continue
            except errors.FloodWaitError:
                await asyncio.sleep(100)
                continue

        await bot.edit_message(event.chat_id, prediction.id, full_prediction, parse_mode='markdown')
    raise events.StopPropagation


@bot.on(events.NewMessage(func=lambda e: e.is_private or e.is_group))
async def on_message(event):
    sender = await event.get_sender()
    if isinstance(sender, types.User): # type: ignore
        language_code = get_language_code(getattr(sender, 'lang_code', 'ru'))
        answer_text = await predictor.translate(language_code, default_answer)
        await event.respond(answer_text)


def run_bot():
    bot.start(bot_token=settings.TOKEN)
    bot.run_until_disconnected()
