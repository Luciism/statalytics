import functools
from typing import Any, Awaitable, Callable, Literal, TypeVar 

from discord import app_commands, Interaction
from discord.app_commands import Cooldown

from helper.autocomplete import username_autocompletion
from helper.cooldowns import generic_command_cooldown


T = TypeVar('T', bound=Callable[..., Awaitable[Any]])

def app_command(
    name: str,
    description: str,
    params: dict[str, str],
    allow_user_installs: bool = True,
    command_cooldown: Literal["generic", None] = "generic",
    autocompletes: dict[
        str,
        Callable[[Interaction, str], Awaitable[list[app_commands.Choice[str]]]]
    ] | None = None
) -> Callable[[T], T]:
    """Decorator factory for creating app commands with common configurations."""
    
    def decorator(command: T) -> T:
        cooldown_func: Callable[[Interaction], Cooldown | None] = {
            "generic": generic_command_cooldown,
            None: lambda _: None
        }.get(command_cooldown)

        autocomplete_fns = autocompletes

        if autocomplete_fns is None:
            autocomplete_fns = {}

        if params.get("player") and not autocomplete_fns.get("player"):
            autocomplete_fns["player"] = username_autocompletion

        @app_commands.command(name=name, description=description)
        @app_commands.describe(**params)
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @app_commands.allowed_installs(guilds=True, users=allow_user_installs)
        @app_commands.autocomplete(**(autocomplete_fns or {}))
        @app_commands.checks.dynamic_cooldown(cooldown_func)
        @functools.wraps(command)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await command(*args, **kwargs)

        return wrapper  # type: ignore
    
    return decorator
