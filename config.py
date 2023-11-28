from dataclasses import dataclass

from environs import Env


@dataclass
class Hidden:
    bot_token: str
    admin_id: list[int]
    yatoken: str


def load_config(path: str = '..env'):
    env = Env()
    env.read_env()
    return Hidden(
        admin_id=list(map(int, env.list("ADMIN_ID"))),
        bot_token=env.str("BOT_TOKEN"),
        yatoken=env.str("YATOKEN")
    )


hidden_vars = load_config()


print(hidden_vars.admin_id)