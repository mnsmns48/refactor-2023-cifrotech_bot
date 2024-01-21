import asyncio

from config import dp, bot, commands
from db_core.engine import async_engine_pg
from db_core.models import metadata
from handlers.admin_handler import admin_, register_admin_handlers
from handlers.user_handler import user_, register_user_handlers


async def main():
    async with async_engine_pg.begin() as connect:
        await connect.run_sync(metadata.create_all)
    register_admin_handlers()
    register_user_handlers()
    dp.include_routers(admin_, user_)
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
