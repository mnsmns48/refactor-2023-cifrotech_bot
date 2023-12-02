import asyncio
import logging

from config import dp, bot, commands
from handlers.admin_handler import admin_
from handlers.user_handler import user_, register_admin_handlers


async def main():
    logging.basicConfig(level=logging.INFO)
    register_admin_handlers()
    dp.include_routers(user_)
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == '__main__':
    try:
        print('Bot went to work')
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot Stopped')
