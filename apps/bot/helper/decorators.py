import functools
from typing import Any, Awaitable, Callable, Literal, TypeVar 

from discord import app_commands, Interaction
from discord.app_commands import Cooldown

import statalib as lib
from statalib.commands import get_command
from helper.autocomplete import Autocomplete 
from helper.cooldowns import generic_command_cooldown


T = TypeVar('T', bound=Callable[..., Awaitable[Any]])
CooldownT = Callable[[Interaction], Cooldown | None]

def update_command_usage_check(command_id: str, should_update: bool=True):
    if should_update is False:
        fake: Callable[[Interaction], Literal[True]] = lambda interaction: True
        return fake 

    def predicate(interaction: Interaction) -> Literal[True]:
        lib.usage.CommandMetricsRepo.update_command_usage(command_id, interaction.user.id)
        return True

    return predicate


def app_command(
    command_id: str,
    update_command_usage: bool=True,
    group: app_commands.Group | None=None
) -> Callable[[T], T]:
    """Decorator factory for creating app commands with common configurations."""
    
    def decorator(command: T) -> T:
        cmd = get_command(command_id)

        autocompletes = {
            arg.name: Autocomplete.by_name(arg.autocomplete)
            for arg in cmd.arguments if arg.autocomplete
        }

        if cmd.cooldown:
            cooldown_fn: CooldownT = generic_command_cooldown
        else:
            cooldown_fn = lambda _: None

        init = group if group else app_commands

        @init.command(name=cmd.name, description=cmd.description)
        @app_commands.describe(**cmd.argument_map())
        @app_commands.allowed_contexts(**cmd.contexts.as_dict())
        @app_commands.allowed_installs(**cmd.installs.as_dict())
        @app_commands.checks.dynamic_cooldown(cooldown_fn)
        @app_commands.check(update_command_usage_check(cmd.id, update_command_usage))
        @app_commands.autocomplete(**autocompletes)
        @functools.wraps(command)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await command(*args, **kwargs)

        return wrapper  # type: ignore
    
    return decorator

